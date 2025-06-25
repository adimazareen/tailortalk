from typing import Dict, TypedDict
from datetime import datetime, timedelta
from langgraph.graph import Graph
from langgraph.prebuilt import ToolNode
from .calendar import get_calendar_service, check_availability, create_event
from .schemas import AppointmentRequest, AppointmentSlot, ConfirmedAppointment

class AgentState(TypedDict):
    request: AppointmentRequest
    available_slots: list[AppointmentSlot]
    confirmed_appointment: ConfirmedAppointment

def parse_user_input(state: AgentState) -> AgentState:
    request = state['request']
    user_input = request.user_input.lower()
    
    # Simple intent detection (in a real app, use NLP)
    if 'schedule' in user_input or 'book' in user_input or 'meeting' in user_input:
        request.intent = 'book_appointment'
    
    # Extract date and time (simplified)
    if 'tomorrow' in user_input:
        request.date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    elif 'friday' in user_input:
        # Find next Friday
        today = datetime.now()
        days_ahead = (4 - today.weekday()) % 7  # 4 is Friday
        request.date = (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
    
    if 'afternoon' in user_input:
        request.time_range = '13:00-17:00'
    elif 'morning' in user_input:
        request.time_range = '09:00-12:00'
    elif '3-5 pm' in user_input:
        request.time_range = '15:00-17:00'
    
    return {'request': request}

def find_available_slots(state: AgentState) -> AgentState:
    request = state['request']
    service = get_calendar_service()
    
    if not request.date:
        return state
    
    # Default to today if no date specified
    date_str = request.date or datetime.now().strftime('%Y-%m-%d')
    date = datetime.strptime(date_str, '%Y-%m-%d')
    
    # Generate potential slots (simplified)
    potential_slots = []
    if request.time_range:
        start_hour, end_hour = map(int, request.time_range.split('-')[0].split(':'))
        for hour in range(start_hour, end_hour):
            start_time = datetime(date.year, date.month, date.day, hour, 0)
            end_time = start_time + timedelta(minutes=30)
            if check_availability(service, start_time, end_time):
                potential_slots.append(AppointmentSlot(start_time=start_time, end_time=end_time))
    else:
        # Check standard business hours
        for hour in range(9, 17):
            start_time = datetime(date.year, date.month, date.day, hour, 0)
            end_time = start_time + timedelta(minutes=30)
            if check_availability(service, start_time, end_time):
                potential_slots.append(AppointmentSlot(start_time=start_time, end_time=end_time))
    
    return {'available_slots': potential_slots[:3]}  # Return top 3 available slots

def confirm_booking(state: AgentState) -> AgentState:
    if not state.get('available_slots'):
        return state
    
    # For simplicity, pick the first available slot
    slot = state['available_slots'][0]
    service = get_calendar_service()
    confirmation_link = create_event(
        service,
        "Meeting with User",
        slot.start_time,
        slot.end_time
    )
    
    confirmed = ConfirmedAppointment(
        summary="Meeting with User",
        start_time=slot.start_time,
        end_time=slot.end_time,
        confirmation_link=confirmation_link
    )
    
    return {'confirmed_appointment': confirmed}

def generate_response(state: AgentState) -> Dict:
    if not state.get('request'):
        return {"response": "I didn't understand that. Could you please rephrase?"}
    
    if state.get('confirmed_appointment'):
        appointment = state['confirmed_appointment']
        return {
            "response": (
                f"Your appointment has been booked from "
                f"{appointment.start_time.strftime('%A, %B %d at %I:%M %p')} to "
                f"{appointment.end_time.strftime('%I:%M %p')}. "
                f"Here's your calendar link: {appointment.confirmation_link}"
            )
        }
    
    if state.get('available_slots'):
        slots = state['available_slots']
        slot_options = "\n".join(
            f"{i+1}. {slot.start_time.strftime('%A, %B %d at %I:%M %p')}" 
            for i, slot in enumerate(slots)
        )
        return {
            "response": (
                "I found these available slots:\n" + slot_options + 
                "\nPlease reply with the number of the slot you'd like to book."
            )
        }
    
    request = state['request']
    if request.intent == 'book_appointment':
        if not request.date:
            return {"response": "When would you like to schedule the appointment?"}
        if not request.time_range:
            return {"response": "What time of day works best for you?"}
    
    return {"response": "I'm here to help you schedule appointments. When would you like to meet?"}

# Create the workflow
workflow = Graph()

# Define nodes
workflow.add_node("parse_input", parse_user_input)
workflow.add_node("find_slots", find_available_slots)
workflow.add_node("confirm_booking", confirm_booking)
workflow.add_node("generate_response", generate_response)

# Define edges
workflow.add_edge("parse_input", "find_slots")
workflow.add_edge("find_slots", "generate_response")
workflow.add_edge("confirm_booking", "generate_response")

# Add conditional edges
def decide_to_confirm(state: AgentState):
    if state.get('available_slots'):
        return "confirm_booking"
    return "generate_response"

workflow.add_conditional_edges(
    "find_slots",
    decide_to_confirm,
    {
        "confirm_booking": "confirm_booking",
        "generate_response": "generate_response",
    },
)

# Set entry and exit points
workflow.set_entry_point("parse_input")
workflow.set_finish_point("generate_response")

# Compile the graph
appointment_agent = workflow.compile()