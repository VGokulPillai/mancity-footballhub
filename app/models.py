"""Pydantic models for the Man City Fan Intelligence Hub data tables."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class DimFan(BaseModel):
    fan_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    age_band: Optional[str] = None
    postcode: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    distance_band: Optional[str] = None
    miles_from_stadium: Optional[float] = None
    is_season_ticket_holder: Optional[bool] = None
    first_timer: Optional[bool] = None
    membership_type: Optional[str] = None


class DimFixture(BaseModel):
    fixture_id: str
    season: Optional[str] = None
    competition: Optional[str] = None
    match_date: Optional[date] = None
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    venue: Optional[str] = None
    kickoff_time: Optional[str] = None
    result: Optional[str] = None


class DimRetailProduct(BaseModel):
    product_id: str
    product_name: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    season: Optional[str] = None


class DimTourEvent(BaseModel):
    tour_event_id: str
    event_name: Optional[str] = None
    event_date: Optional[date] = None
    event_type: Optional[str] = None
    venue: Optional[str] = None
    capacity: Optional[int] = None


class FactTicketingTransaction(BaseModel):
    transaction_id: str
    fan_id: Optional[str] = None
    fixture_id: Optional[str] = None
    ticket_area: Optional[str] = None
    price_type: Optional[str] = None
    seat_location: Optional[str] = None
    sale_method: Optional[str] = None
    ticket_price: Optional[float] = None
    quantity: Optional[int] = None
    transaction_date: Optional[date] = None
    season: Optional[str] = None
    is_season_ticket: Optional[bool] = None
    is_one_off: Optional[bool] = None


class FactEngagement(BaseModel):
    engagement_id: str
    fan_id: Optional[str] = None
    channel: Optional[str] = None
    engagement_type: Optional[str] = None
    engagement_date: Optional[date] = None
    content_category: Optional[str] = None


class FactEngagementGroup(BaseModel):
    group_id: str
    group_name: Optional[str] = None
    engagement_count: Optional[int] = None
    fan_count: Optional[int] = None


class FactRetailTransaction(BaseModel):
    transaction_id: str
    fan_id: Optional[str] = None
    product_id: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    total_amount: Optional[float] = None
    transaction_date: Optional[date] = None
    channel: Optional[str] = None
    season: Optional[str] = None


class FactRetailDiscount(BaseModel):
    discount_id: str
    product_id: Optional[str] = None
    discount_type: Optional[str] = None
    discount_percentage: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class FactMembershipTransaction(BaseModel):
    transaction_id: str
    fan_id: Optional[str] = None
    membership_type: Optional[str] = None
    amount: Optional[float] = None
    transaction_date: Optional[date] = None
    season: Optional[str] = None
    status: Optional[str] = None


class FactCityplusTransaction(BaseModel):
    transaction_id: str
    fan_id: Optional[str] = None
    content_type: Optional[str] = None
    platform: Optional[str] = None
    transaction_date: Optional[date] = None
    amount: Optional[float] = None


class FactTourTransaction(BaseModel):
    transaction_id: str
    fan_id: Optional[str] = None
    tour_event_id: Optional[str] = None
    quantity: Optional[int] = None
    amount: Optional[float] = None
    transaction_date: Optional[date] = None


class FactZendeskTicket(BaseModel):
    ticket_id: str
    fan_id: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    created_date: Optional[date] = None
    resolved_date: Optional[date] = None
    satisfaction_rating: Optional[str] = None


class FactZendeskCategory(BaseModel):
    category_id: str
    category_name: Optional[str] = None
    parent_category: Optional[str] = None
    ticket_count: Optional[int] = None


TABLE_MAP = {
    "out_dim_fans": DimFan,
    "out_dim_fixtures": DimFixture,
    "out_dim_retail_products": DimRetailProduct,
    "out_dim_tour_events": DimTourEvent,
    "out_fact_ticketing_transactions": FactTicketingTransaction,
    "out_fact_engagements": FactEngagement,
    "out_fact_engagement_group": FactEngagementGroup,
    "out_fact_retail_transactions": FactRetailTransaction,
    "out_fact_retail_discounts": FactRetailDiscount,
    "out_fact_membership_transactions": FactMembershipTransaction,
    "out_fact_cityplus_transactions": FactCityplusTransaction,
    "out_fact_tour_transactions": FactTourTransaction,
    "out_fact_zendesk_tickets": FactZendeskTicket,
    "out_fact_zendesk_category": FactZendeskCategory,
}
