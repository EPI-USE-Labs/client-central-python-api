import pytest
from aiohttp import web

import asyncio
import clientcentral.query as operators
from clientcentral.clientcentral import ClientCentral
from clientcentral.model.Status import Status
from clientcentral.Exceptions import (
    ButtonNotAvailable,
    ButtonRequiresComment,
    HTTPError,
    DateFormatInvalid,
)

import aiohttp
import asyncio
from aioresponses import aioresponses

import json

async_cc = ClientCentral(
    production=False,
    token="12345-ABCABC-ABCABCABCABCAB-1A_ABCABCABCAB_ABC_ABCABCABCABCABCAB",
    run_async=True,
)


@pytest.fixture
def mock_aioresponse():
    with aioresponses() as m:
        yield m


get_by_id_requst_url = "https://qa.clientcentral.io/api/v1/tickets/123.json?select=subject%252Cdescription%252Cpriority.name%252Cstatus.name%252Cstatus.closed%252Cevents.event_changes.name%252Ccustomer_user.%252A%252Ctype.name%252Cevents.comment%252Cevents.created_by_user.first_name%252Cevents.created_by_user.last_name%252Cevents.created_by_user.title%252Cevents.created_by_user.job_title%252Cevents.created_by_user.email%252Cevents.created_at%252Ccreated_by_user.email%252Ccreated_by_user.title%252Ccreated_by_user.job_title%252Ccreated_by_user.first_name%252Ccreated_by_user.last_name%252Cuser_watchers.email%252Cuser_watchers.first_name%252Cuser_watchers.last_name%252Cuser_watchers.title%252Cuser_watchers.job_title%252Cevents.event_changes.to_value%252Cevents.event_changes.from_value%252Cevents.internal%252Cassignee%252C%252A&token=12345-ABCABC-ABCABCABCABCAB-1A_ABCABCABCAB_ABC_ABCABCABCABCABCAB"

get_by_id_raw_response = '{"data":{"id":123,"type":{"id":9,"_type":"TicketType","name":"Service request"},"project":{"id":43,"_type":"TicketProject"},"workspace":{"id":87,"_type":"Workspace"},"created_by_user":{"id":14012,"_type":"User","title":{"id":5,"name":"master","human_name":"Master","_type":"Title"},"email":"thomas@labs.epiuse.com","first_name":"Thomas","last_name":"Scholtz","job_title":"Software Engineer"},"status":{"id":1,"_type":"TicketStatus","closed":false,"name":"New"},"priority":{"id":3,"_type":"TicketPriority","name":"P3 Medium"},"account":{"id":1,"_type":"Account"},"customer_user":{"id":14012,"_type":"User","account":{"id":1,"_type":"Account"},"roles":[{"id":352,"_type":"Role"},{"id":1850,"_type":"Role"},{"id":10187,"_type":"Role"},{"id":12160,"_type":"Role"},{"id":12680,"_type":"Role"},{"id":12744,"_type":"Role"},{"id":13153,"_type":"Role"},{"id":13159,"_type":"Role"},{"id":13290,"_type":"Role"},{"id":13293,"_type":"Role"},{"id":13320,"_type":"Role"},{"id":13396,"_type":"Role"},{"id":13410,"_type":"Role"},{"id":13696,"_type":"Role"},{"id":13697,"_type":"Role"},{"id":13830,"_type":"Role"},{"id":14459,"_type":"Role"},{"id":14490,"_type":"Role"}],"profile":{"id":14008,"_type":"UserProfile"},"email_campaigns":[{"id":11,"_type":"EmailCampaign"},{"id":14,"_type":"EmailCampaign"},{"id":17,"_type":"EmailCampaign"},{"id":20,"_type":"EmailCampaign"},{"id":23,"_type":"EmailCampaign"},{"id":26,"_type":"EmailCampaign"},{"id":29,"_type":"EmailCampaign"},{"id":32,"_type":"EmailCampaign"},{"id":35,"_type":"EmailCampaign"},{"id":37,"_type":"EmailCampaign"}],"title":{"id":5,"name":"master","human_name":"Master","_type":"Title"},"email":"thomas@labs.epiuse.com","first_name":"Thomas","last_name":"Scholtz","locked":false,"last_sign_in_at":"2021-08-05T15:03:53Z","locale":"en","number":13962,"office_number":"","mobile_number":"+27780360680","job_title":"Software Engineer","activities_count":1362,"activities_temporal_count":431,"name":"Thomas Scholtz","solution_field":[]},"assignee":{"id":12744,"_type":"Role"},"reported_version":null,"reported_build":null,"target_version":null,"target_build":null,"sla_policy":null,"events":[{"id":1178337,"_type":"TicketEvent","created_by_user":null,"event_changes":[{"id":1078317,"_type":"TicketEventChange","name":"assignee","from_value":"","to_value":"Role:12744"}],"comment":"","internal":true,"created_at":"2021-08-05T14:54:07Z"}],"attachments":[],"user_watchers":[],"role_watchers":[],"sla":null,"time_log_entries":[],"original_locale":null,"subject":"Some magical test ticket","description":"<div>TEST</div>","internal":false,"created_at":"2021-08-05T14:54:07Z","updated_at":"2021-08-05T14:54:08Z","created_by_name":null,"created_by_email":null,"responded_at":"2021-08-05T14:54:07Z","resolved_at":null,"assignee_roles":[{"id":12744,"_type":"Role"}],"last_event":{"id":1178337,"_type":"TicketEvent"},"last_user_event":null,"previous_status":null,"offering_accesses":[{"id":45390,"_type":"OfferingAccess"},{"id":40741,"_type":"OfferingAccess"}],"related_tickets":[],"time_log_entries_duration":0,"visible_to_customer":true,"slo_sys_required":null,"existing_customer":null,"ccat_related_tp":null,"motivation_no_labs_system":null,"sloa_reviewer":null,"slo_cloud_storage":null,"slo_sap_source":null,"testing":[],"deal_contact_list":[],"test_attendance":[],"test_count":null,"delivery_type":null,"doc_update_required":null,"deal_start_date":null,"ms_approval_sbg":[],"test_field_3":null,"qg_version":null,"test_api":[],"supported_sap_version":[],"sbsa_delivery_date":null,"sbsa_nr_employees":null,"ccat_tp_info":[],"sa2_system_product_info":[],"previous_assignee":null,"due_date":null,"test_field_2":null,"test_start":null,"internal_it_category":{"id":374,"name":"Other","_type":370},"test_training_name":[],"ticket_test":null,"transport_number":null,"vm_milestone":null,"sku_list":[],"ccat_tp_status":[],"license_exchange_comment":null,"sa2_engagement_context":null,"sa2_system_reports_for_review":[],"cancellation_reason_b":null,"delivery_date":null,"billing_address":null,"lt_oap_ref":null,"eval_agrmnt":[],"solution":null,"sprint_start_date":null,"target_date":null,"sources_required":null,"twb_proj_number":null,"sa2_web_ticket":null,"ms_retainer":null,"sbsa_ecc_sid":[],"sa2_abap_ticket":null,"sbsa_system_type":null,"ms_category":null,"screenshots_1":[],"license_extension_request":[],"sa2_test_qa_effort":null,"sap_tested_on":[],"sa2_hcm_review_perspectives_other":null,"sbsa_country":null,"sbsa_functional_area":null,"sbsa_tp_approval":[],"license_change_reason":null,"up_team":null,"sbsa_approvals":[],"installation_no_change_reason":null,"quote_optional":null,"sbsa_cr_number":null,"ccat_tp_scenario":null,"ccat_tp_type":null,"sbsa_change_reason":null,"test_ticket":null,"sbsa_resources":[],"sa2_s4ha_review_perspectives":[],"sap_land":null,"cc_link":null,"netsuite_customer":null,"po_contact_email":null,"quote":null,"sbsa_batch_name":null,"text_type":null,"sbsa_test_cycle":null,"sbsa_test_env":null,"sbsa_test_case_line_type":[],"sbsa_target":[],"sbsa_category":null,"test_field":[],"sa2_dsm_review_perspectives_other":null,"sa2_s4h_review_perspectives_other":null,"sa2_slo_review_perspectives_other":null,"sa2_hcma_review_perspectives":[],"sbsa_tp_basis_approval":null,"sa_reported_build":null,"sbsa_batch_boolean":null,"netsuite_bill_to_customer":null,"notes":null,"cla_scope":[],"footprints_number":null,"regr_test_status":null,"dev_transport":null,"sbsa_defect_type":null,"sbsa_project_number":null,"pending":null,"invoice_number":null,"internal_it_affected_users":[{"id":14012,"_type":"User"}],"sa_engagement_start_date":null,"oap_category":[],"patch_status":null,"patch_type":null,"rank":null,"sap_sid":null,"test_steps":null,"transport_date":null,"cc_category":null,"sa2_sloa_review_perspectives":[],"ccat_failed_tp":null,"sbsa_tp_technical_approval":null,"workload":null,"auto_generate_eval_key":null,"sbsa_incident_number":null,"est_cost":null,"test_case_id":null,"valid_for_build":null,"valid_for_release":[],"basis_customer":null,"cancellation_reason":null,"euuk_project_name":null,"euuk_project_type":[],"euuk_target_date":null,"correction":null,"internal_mac_address":null,"invoice_paid":null,"steps":null,"ms_atuo_rating":null,"ms_landscape":null,"sloa_status":null,"system_owner":null,"internal_mailing_list_name":null,"ms_centos_version":[],"proj_related":null,"security_related":false,"file_type":[],"git_branch":null,"ms_cr_category":null,"prod_dev_lead":null,"reseller":null,"screenshots":[],"sow_draft":[],"supported_sap_version_new":[],"upsource_id":null,"region":[],"language_review_status":null,"sa_data_file_version":null,"categorization_of_change":null,"defect_classification":null,"est_slo_end":null,"legal_agrmnt":[],"service_owner":null,"dischem_fnr_sid":[],"escalation_line":null,"build":null,"ms_backup":[],"atf_replicate_issue_script":null,"eula_addendnum":[],"ms_testers":[],"changelog_text":null,"po_contact_telno":null,"collector":null,"due_date_cr":null,"campaign":null,"sap_version":[],"ms_linux_comp":null,"pex_portal_category":null,"scheduled_time":null,"slo_classification":null,"terminate_user":[],"new_sku_display_name":null,"dsm_oap_analysis_type":[],"prerequisites":null,"account_customer":null,"slo_sap_target":null,"kb_used":[],"dsm_product":null,"new_sku_name":null,"sku_product":null,"hr_category":null,"isphere_category":null,"ms_linux_dis":null,"ms_sap_product_sp":null,"product":[],"test_effort":[],"vm_category":null,"change_control":[],"downtime_required":null,"euuk_start_date":null,"ms_solution_partner":null,"project_contact":null,"dual_maintained":[],"exp_cat":null,"git_branch_from":null,"ignore_errors":null,"ms_os":null,"strict_import_time":null,"estimated_hours":null,"developer":null,"product_portfolio":null,"bifrost_source_control":[],"exp_currency":null,"iow_system_type":null,"platform":null,"target_product":null,"has_parameters":null,"dischem_fiori_sid":[],"dischem_solman_sid":[],"include_in_change_log":null,"parent":null,"db_size":null,"expro_build_number":null,"expro_data_dependent":null,"images":null,"ms_db2_v":null,"abap_program":[],"collector_type":null,"data_file":[],"ms_fp":null,"ms_os_db2":[],"sku_change":[],"sku_name":null,"ms_sap_patch":null,"marketing_request_type":null,"assigned_tester":null,"build_tested":null,"flow_app":null,"host_name":null,"milestone":null,"mt_customer_number":null,"pex_p_milestone":null,"sap_area":null,"master_ticket":null,"origin":null,"qcs_task_type":null,"client_central_suggestion":null,"code_reviewer":null,"ccat_system_type":null,"change_frequency":null,"data_previews":[],"eula_signed_a":[],"license_key_days":null,"customer_action":null,"dischem_projects":null,"end_window":null,"incident_ref":null,"internal_it_automatic_access_request_affected_user":null,"languages":[],"ms_comp":null,"ms_linux_other":null,"sa_transport_number":null,"dischem_ecc_sid":[],"dischem_ewm_sid":[],"doc_type":[],"internal_it_vpn_choice":null,"temporary_workaround":null,"dischem_system_type":null,"internal_it_automatic_access_request":null,"qa_lead":[],"abap_class":[],"abap_method_dev_int_lib":[],"abap_method_imp":[],"abap_package":[],"aberdare_ecc_sid":[],"aberdare_system_type":null,"at_milestone":[],"ccat_ecc_sid":[],"change_location":null,"adapter_generator_source_file":[],"atf_script_expected_to_pass":null,"auto_product_tickets":null,"azure_work_item_id":null,"bifrost_milestone":null,"euuk_system":[],"exp_approver":null,"flow_milestone":null,"frequency_of_change":null,"iow_ecc_sid":[],"ms_auto_affected_customer":null,"ms_auto_products":null,"ms_changelink":null,"ms_changemodel":null,"ms_comp_version":null,"ms_db":null,"ms_db2_v2":[],"ms_patch_type":null,"ms_prod":null,"ms_rhel_version":[],"ms_sap_product":null,"ms_suse_version":[],"ms_windows":[],"oap_engine_category":[],"expected_end_date":null,"regression_testing":[],"rms_del_entries":null,"invoice_approved_by":null,"invoice_contact_email":null,"invoice_contact_name":null,"invoice_contact_telno":null,"invoice_issued":null,"rms_tags":[],"sa2_backup_tp_num":null,"sa2_code_rev_effort":null,"sa2_code_tp_num":null,"sa2_content_tp_num":null,"sa2_del_tp_num":null,"sa2_grouping":[],"licence_req_type":null,"ms_backup_retention":null,"ms_hostname":null,"ms_inctoprob":null,"new_sku_inc_accnt":null,"payment_due":null,"pmnt_date":null,"po_contact_name":null,"po_file":[],"po_received":null,"prod_dev_lead_sku":null,"project_active":null,"sap_change_control":null,"sku_display_name":null,"sku_inc_accnt":null,"dischem_bw_sid":[],"dischem_crm_sid":[],"dischem_full_landscape":[],"dischem_hr_sid":[],"dischem_sandbox_sid":[],"dischem_test_sid":[],"est_slo_start":null,"eu_uk_customer_if_external":null,"project_notes":null,"qa_tester":null,"quote_signed":[],"quote_signed_non_required":[],"retestable":null,"slo_type":null,"solution_attachment":[],"vat_number":null,"sources":null,"supports_field_sets":null,"tech_collector_name":null,"sow_ref":null,"splunk_component":null,"start_window":null,"test_field1":null,"transport_ids":null,"test_field_1":null,"ui_mock_ups":[],"word_count":null}}'

get_buttons_avail_request_url = "https://qa.clientcentral.io/api/v1/tickets/123/available_buttons.json?token=12345-ABCABC-ABCABCABCABCAB-1A_ABCABCABCAB_ABC_ABCABCABCABCABCAB"
get_buttons_avail_response = '{"page":1,"more":false,"total_pages":1,"data":[{"id":477,"colour":{"id":4,"name":"neutral","human_name":"Neutral","_type":"StatusColour"},"agent_only":false,"require_comment":true,"enabled":true,"name":"Comment"},{"id":478,"colour":{"id":1,"name":"positive","human_name":"Positive","_type":"StatusColour"},"agent_only":true,"require_comment":false,"enabled":true,"name":"Grab"}]}'


def test_incorrect_date_format_request(mock_aioresponse):
    ticket_response_body_dict = json.loads(get_by_id_raw_response)
    ticket_response_body_dict["data"]["created_at"] = "2021-01-01 00:00:00 UTC"

    mock_aioresponse.get(
        get_by_id_requst_url,
        status=200,
        body=json.dumps(ticket_response_body_dict),
    )

    mock_aioresponse.get(
        get_buttons_avail_request_url,
        status=200,
        body=get_buttons_avail_response,
    )

    try:
        loop = async_cc._event_loop
        print(loop)
        # assert loop == asyncio.get_running_loop()
        ticket = loop.run_until_complete(async_cc.get_ticket_by_id(123))
        assert ticket.subject == "Some magical test ticket"
        assert False
    except DateFormatInvalid as e:
        assert True


def test_correct_date_format_1_request(mock_aioresponse):
    ticket_response_body_dict = json.loads(get_by_id_raw_response)
    ticket_response_body_dict["data"]["created_at"] = "2021-01-01T00:00:00Z"
    ticket_response_body_dict["data"]["updated_at"] = "2021-01-01T00:00:00Z"

    loop = async_cc._event_loop
    mock_aioresponse.get(
        get_by_id_requst_url,
        status=200,
        body=json.dumps(ticket_response_body_dict),
    )

    mock_aioresponse.get(
        get_buttons_avail_request_url,
        status=200,
        body=get_buttons_avail_response,
    )

    ticket = loop.run_until_complete(async_cc.get_ticket_by_id(123))
    assert ticket.subject == "Some magical test ticket"
    assert (
        ticket.created_at.strftime("%Y-%m-%dT%H:%M:%S%z") == "2021-01-01T00:00:00+0000"
    )
    assert (
        ticket.updated_at.strftime("%Y-%m-%dT%H:%M:%S%z") == "2021-01-01T00:00:00+0000"
    )


def test_correct_date_format_2_request(mock_aioresponse):
    ticket_response_body_dict = json.loads(get_by_id_raw_response)
    ticket_response_body_dict["data"]["created_at"] = "2021-01-01T00:00:00.000000Z"
    ticket_response_body_dict["data"]["updated_at"] = "2021-01-01T00:00:00.000000Z"

    loop = async_cc._event_loop
    mock_aioresponse.get(
        get_by_id_requst_url,
        status=200,
        body=json.dumps(ticket_response_body_dict),
    )

    mock_aioresponse.get(
        get_buttons_avail_request_url,
        status=200,
        body=get_buttons_avail_response,
    )

    ticket = loop.run_until_complete(async_cc.get_ticket_by_id(123))
    assert ticket.subject == "Some magical test ticket"
    assert (
        ticket.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        == "2021-01-01T00:00:00.000000+0000"
    )
    assert (
        ticket.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        == "2021-01-01T00:00:00.000000+0000"
    )
