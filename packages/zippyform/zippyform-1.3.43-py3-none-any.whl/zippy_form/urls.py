from django.urls import path

from zippy_form.views import form_list, create_form, update_form, delete_form, \
    form_submission_list, steps_mapped_to_form, create_form_step, delete_form_step, fields_mapped_to_form_step, \
    map_field_to_form_step, re_order_field, delete_field, update_field_settings, \
    dynamic_form_fields_mapped_to_form_step, submit_form, update_form_status, update_form_step, dynamic_form_list, \
    create_account, account_list, form_submission_details, delete_form_submission, create_webhook, webhook_list, \
    webhook_detail, update_webhook, delete_webhook, update_webhook_status, update_form_name, \
    form_payment_settings_stripe_connect, get_form_payment_settings, update_form_payment_settings, \
    get_form_active_number_fields, update_account_payment_details, update_account_profile_details, \
    create_payment_gateway_webhook, get_payment_gateway_webhook_list, \
    form_submission_details2, form_submission_details3, get_account_details, webhook_stripe, \
    form_list_without_pagination, get_form_gsheet_url, get_form_meta_details, \
    update_form_submission_meta_data_value

urlpatterns = [
    path('builder/account/list', account_list),
    path('builder/account/create', create_account),
    path('builder/account/<uuid:account_id>/get-details', get_account_details),
    path('builder/account/<uuid:account_id>/update-profile-details', update_account_profile_details),
    path('builder/account/<uuid:account_id>/update-payment-details', update_account_payment_details),
    path('builder/form/list', form_list),
    path('builder/form/list_without_pagination', form_list_without_pagination),
    path('builder/form/create', create_form),
    path('builder/step/create', create_form_step),
    path('builder/map-field', map_field_to_form_step),
    path('builder/<uuid:form_id>//meta-details/<meta_data_slug>', get_form_meta_details),
    path('builder/<uuid:form_id>/gsheet-url', get_form_gsheet_url),
    path('builder/<uuid:form_id>/update', update_form),
    path('builder/<uuid:form_id>/update-form-name', update_form_name),
    path('builder/<uuid:form_id>/update-form-status', update_form_status),
    path('builder/<uuid:form_id>/delete', delete_form),
    path('builder/<uuid:form_id>/submission/list', form_submission_list),
    path('builder/<uuid:form_id>/submission/<uuid:form_submission_id>', form_submission_details),
    path('builder/<uuid:form_id>/submission_detail/<uuid:form_submission_id>', form_submission_details2),
    path('builder/<uuid:form_id>/submission_detail/<uuid:form_submission_id>/via-field_slugs', form_submission_details3),
    path('builder/<uuid:form_id>/submission/<uuid:form_submission_id>/delete', delete_form_submission),
    path('builder/<uuid:form_id>/steps', steps_mapped_to_form),
    path('builder/<uuid:form_id>/fields', fields_mapped_to_form_step),
    path('builder/<uuid:step_id>/update-form-step', update_form_step),
    path('builder/<uuid:step_id>/delete-form-step', delete_form_step),
    path('builder/<uuid:form_id>/fields/<uuid:step_id>', fields_mapped_to_form_step),
    path('builder/<uuid:form_id>/<uuid:step_id>/<uuid:field_id>/re-order-field', re_order_field),
    path('builder/<uuid:form_id>/<uuid:field_id>/delete-field', delete_field),
    path('builder/<uuid:form_id>/active_number_fields', get_form_active_number_fields),
    path('builder/<uuid:form_id>/<uuid:field_id>/update-field-settings', update_field_settings),
    path('builder/form/payment_settings/<uuid:form_id>/details', get_form_payment_settings),
    path('builder/form/payment_settings/<uuid:form_id>/details/<payment_gateway>/<payment_mode>', get_form_payment_settings),
    path('builder/form/payment_settings/<uuid:form_id>', update_form_payment_settings),
    path('builder/form/payment_settings/stripe_connect', form_payment_settings_stripe_connect),
    path('builder/payment_gateway/webhook/create', create_payment_gateway_webhook),
    path('builder/payment_gateway/webhook/list/<payment_gateway>/<payment_mode>', get_payment_gateway_webhook_list),
    path('builder/webhook/create', create_webhook),
    path('builder/webhook/list', webhook_list),
    path('builder/webhook/<uuid:webhook_id>/detail', webhook_detail),
    path('builder/webhook/<uuid:webhook_id>/update', update_webhook),
    path('builder/webhook/<uuid:webhook_id>/delete', delete_webhook),
    path('builder/webhook/<uuid:webhook_id>/update-webhook-status', update_webhook_status),
    path('dynamic-form/list', dynamic_form_list),
    path('dynamic-form/<uuid:form_id>/fields', dynamic_form_fields_mapped_to_form_step),
    path('dynamic-form/<uuid:form_id>/fields/<uuid:step_id>', dynamic_form_fields_mapped_to_form_step),
    path('dynamic-form/<uuid:form_id>/submit/<uuid:step_id>', submit_form),
    path('dynamic-form/<uuid:form_id>/submit/<uuid:step_id>/<uuid:submission_id>', submit_form),
    path('dynamic-form/<uuid:form_id>/<uuid:submission_id>/update-meta-value/<uuid:meta_data_id>', update_form_submission_meta_data_value),
    path('dynamic-form/webhook/listen/stripe', webhook_stripe),
]
