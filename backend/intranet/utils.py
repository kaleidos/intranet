#!/usr/bin/python
# -*- coding: utf-8 -*-


def clear_model_dict(data, hidden_fields=['password']):
    new_dict = {}
    for key, val in data.items():
        if not key.startswith('_') and key not in hidden_fields:
            new_dict[key] = val
    return new_dict


def get_consumed_days_for_user(user, holidays_year):
    from .models import STATE_ACCEPTED
    return sum([holiday_req.count_working_days() for holiday_req in user.holidays_requests.filter(year=holidays_year, status=STATE_ACCEPTED)])


def get_requested_days_for_user(user, holidays_year):
    from .models import STATE_CREATED
    return sum([holiday_req.count_working_days() for holiday_req in user.holidays_requests.filter(year=holidays_year, status=STATE_CREATED)])
