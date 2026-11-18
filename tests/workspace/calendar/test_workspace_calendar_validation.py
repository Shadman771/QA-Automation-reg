"""Workspace > Calendar - Create New Event validation, negative, boundary
and the Multiple Events (bulk upload) tab. Anything that could save an
event writes its unique tag into the description and cleans up in
`finally`. Nothing is ever uploaded through Multiple Events."""
import pytest

from tests.workspace._flows import (
    create_event, fill_event, finish, live_country, mk, open_calendar, open_create_event, uid,
)
from utils.wait import wait_for_content

FEATURE = "Workspace Calendar"

MISSING_CASES = [
    ("21", "Select Country", "country", "Country name is required"),
    ("22", "Nature of Compliance", "title", "Title is required"),
    ("23", "Due Date", "due", "Due date is required"),
]


@pytest.mark.regression
@pytest.mark.parametrize("num,label,missing,message", MISSING_CASES, ids=[c[2] for c in MISSING_CASES])
def test_workspacecalendar_single_missing_required_field_blocks_save(page, result, num, label, missing, message):
    tag = uid("req")
    case = mk(page, f"WorkspaceCalendar_{num}", FEATURE, f"Saving without {label} shows only that field's error",
              f"With every other field filled and only {label} empty, Save must show '{message}' (and no other "
              "required-field error), keep the modal open, and create no event.",
              f"1. Open Create New Event\n2. Fill everything except {label}\n3. Click Save\n"
              "4. Verify the single error and that the modal is still open\n5. Cancel and verify no row was created",
              f"Missing field: {label}")
    cal = open_calendar(case, page)
    try:
        country = live_country(cal)
        open_create_event(case, cal)
        fill_event(case, cal,
                   country=None if missing == "country" else country,
                   title=None if missing == "title" else tag,
                   description=f"desc {tag}",
                   days=None if missing == "due" else 20)
        case.click(cal.modal_save_button, "'Save' button")
        page.wait_for_timeout(800)
        errors = {"country": cal.modal_country_required_error.count() > 0,
                  "title": cal.modal_title_required_error.count() > 0,
                  "due": cal.modal_due_date_required_error.count() > 0}
        only = errors[missing] and not any(v for k, v in errors.items() if k != missing)
        open_ = cal.modal_title_input.is_visible()
        case.check(f"Only '{message}' is shown and the modal stays open", only and open_,
                   expected=f"only {missing} error, modal open", actual=f"errors={errors}, modal open={open_}")
        case.click(cal.delete_cancel_button, "'Cancel' button")
        cal.wait_modal_closed(10000)
        page.wait_for_timeout(800)
        rows = cal.row(tag).count()
        ok = only and open_ and rows == 0
        case.check("No event was created", rows == 0, expected=0, actual=rows)
        finish(case, result, ok, f"Save was blocked with '{message}' and nothing was created.",
               f"Validation wrong: errors={errors}, modal open={open_}, rows created={rows}.")
    finally:
        cal.delete_all_matching(tag)


@pytest.mark.regression
def test_workspacecalendar_24_whitespace_only_title_must_be_rejected(page, result):
    tag = uid("blank")
    case = mk(page, "WorkspaceCalendar_24", FEATURE, "A whitespace-only Nature of Compliance must be rejected",
              "Nature of Compliance is a required field, so a value of only spaces must be treated as empty: Save "
              "must show 'Title is required' and create nothing. KNOWN APPLICATION DEFECT (confirmed live on RC): "
              "the app accepts it and saves an event with a blank title - this test fails until that is fixed.",
              "1. Open Create New Event\n2. Enter spaces as the title, fill the other fields\n3. Click Save\n"
              "4. Verify 'Title is required' is shown and no blank-titled event was created",
              f"Title: '    '; Description: desc {tag}")
    cal = open_calendar(case, page)
    try:
        open_create_event(case, cal)
        fill_event(case, cal, live_country(cal), "    ", f"desc {tag}", days=20)
        case.click(cal.modal_save_button, "'Save' button")
        page.wait_for_timeout(2500)
        error = cal.modal_title_required_error.count() > 0
        if cal.modal_wrapper.count():
            cal.close_create_event_modal()
            cal.wait_modal_closed(10000)
        page.wait_for_timeout(800)
        created = cal.row(f"desc {tag}").count()
        title = cal.row_cells(f"desc {tag}").get("Nature of Compliance") if created else None
        ok = error and created == 0
        case.check("'Title is required' is shown and no event is created", ok,
                   expected="error shown, 0 events", actual=f"error shown={error}, events created={created}, "
                                                            f"stored title={title!r}")
        finish(case, result, ok, "Whitespace-only title was rejected.",
               f"APPLICATION DEFECT: a whitespace-only title was accepted - error shown={error}, "
               f"{created} event(s) saved with title {title!r}. (The test's own event was deleted afterwards.)")
    finally:
        cal.delete_all_matching(tag)


@pytest.mark.regression
def test_workspacecalendar_25_special_characters_and_long_text_are_stored_intact(page, result):
    tag = uid("special")
    title = tag + " <b>&\"'% ñ中文 " + "L" * 150
    desc = f"desc {tag} <i>x</i> & \"quoted\""
    case = mk(page, "WorkspaceCalendar_25", FEATURE, "Special characters and long text are stored intact in an event",
              "A 190+ character title with markup, quotes, an ampersand, accents and CJK characters (and a "
              "description with markup) must be saved and displayed exactly as typed.",
              "1. Create an event with the special/long title and description\n2. Verify both cells are identical",
              f"Title length: {len(title)}")
    cal = open_calendar(case, page)
    try:
        saved = create_event(case, cal, live_country(cal), title, desc)
        cal.wait_row(tag, 20000)
        cells = cal.row_cells(tag)
        ok = saved and cells.get("Nature of Compliance") == title and cells.get("Description") == desc
        case.check("Title and description equal what was typed", ok, expected=f"{len(title)}-char title + description",
                   actual=f"title ok={cells.get('Nature of Compliance') == title}, "
                          f"description ok={cells.get('Description') == desc}", locator=cal.row(tag))
        finish(case, result, ok, "Special characters and long text were stored intact.",
               f"Stored values differed: title='{cells.get('Nature of Compliance')}', description='{cells.get('Description')}'.")
    finally:
        cal.delete_all_matching(tag)


@pytest.mark.regression
def test_workspacecalendar_26_cancel_discards_a_filled_form(page, result):
    tag = uid("cancel")
    case = mk(page, "WorkspaceCalendar_26", FEATURE, "Cancel discards a completely filled event form",
              "Filling every field and clicking Cancel must close the modal without creating an event; re-opening "
              "the modal must show an empty form.",
              "1. Record the row count\n2. Fill the whole Create New Event form\n3. Cancel\n"
              "4. Verify no row was added\n5. Re-open the modal and verify it is empty", f"Title: {tag}")
    cal = open_calendar(case, page)
    try:
        baseline = cal.agenda_row_count()
        open_create_event(case, cal)
        fill_event(case, cal, live_country(cal), tag, f"desc {tag}", days=20, link="https://example.com/qa")
        case.click(cal.delete_cancel_button, "'Cancel' button")
        closed = cal.wait_modal_closed(10000)
        page.wait_for_timeout(1000)
        rows, count = cal.row(tag).count(), cal.agenda_row_count()
        case.check("No event was created", rows == 0 and count == baseline, expected=f"{baseline} rows",
                   actual=f"{count} rows, {rows} matching")
        open_create_event(case, cal)
        empty = (cal.modal_title_input.input_value(), cal.modal_description_input.input_value(),
                 cal.modal_due_date_input.input_value(), cal.modal_external_link_input.input_value())
        ok = closed and rows == 0 and count == baseline and empty == ("", "", "", "")
        case.check("Re-opened form is empty", empty == ("", "", "", ""), expected="all empty", actual=str(empty))
        case.click(cal.delete_cancel_button, "'Cancel' button")
        finish(case, result, ok, "Cancel discarded the filled form.",
               f"Cancel flow wrong: closed={closed}, rows {baseline}->{count}, matching={rows}, re-opened form={empty}.")
    finally:
        cal.delete_all_matching(tag)


@pytest.mark.regression
def test_workspacecalendar_27_errors_clear_and_save_succeeds_after_correction(page, result):
    tag = uid("fix")
    case = mk(page, "WorkspaceCalendar_27", FEATURE, "After a failed Save, completing the form saves the event",
              "Saving an empty form shows the three required errors; filling the fields in the same modal and "
              "saving again must succeed and list the event (the earlier failure must not block it).",
              "1. Open Create New Event and Save empty\n2. Verify three errors\n3. Fill the form and Save\n"
              "4. Verify the event is listed", f"Title: {tag}")
    cal = open_calendar(case, page)
    try:
        country = live_country(cal)
        open_create_event(case, cal)
        case.click(cal.modal_save_button, "'Save' button (empty form)")
        errors = wait_for_content(cal.modal_title_required_error, timeout=5000) and \
            cal.modal_country_required_error.count() > 0 and cal.modal_due_date_required_error.count() > 0
        case.check("All three required errors are shown", errors, expected="3 errors", actual=errors)
        fill_event(case, cal, country, tag, f"desc {tag}", days=20)
        case.click(cal.modal_save_button, "'Save' button (completed form)")
        closed = cal.wait_modal_closed(20000)
        shown = cal.wait_row(tag, 20000)
        ok = errors and closed and shown
        case.check("Event is saved and listed after the correction", closed and shown, expected="listed",
                   actual=f"modal closed={closed}, row shown={shown}", locator=cal.row(tag))
        finish(case, result, ok, "The corrected form saved successfully.",
               f"Recovery failed: errors shown={errors}, modal closed={closed}, row shown={shown}.")
    finally:
        cal.delete_all_matching(tag)


@pytest.mark.regression
def test_workspacecalendar_28_multiple_events_tab_offers_upload_and_cancels_cleanly(page, result):
    case = mk(page, "WorkspaceCalendar_28", FEATURE, "Multiple Events tab offers an Excel upload; Cancel changes nothing",
              "The Multiple Events tab must replace the single-event fields with an 'Upload Excel File' area, an "
              "unchecked 'Replace the existing events with new events' option, a template download and an Add "
              "button. Cancel must leave the Agenda unchanged. (Nothing is uploaded: a bulk import/replace cannot "
              "be undone.)",
              "1. Record the row count\n2. Create New Event > Multiple Events\n3. Verify the upload controls\n"
              "4. Cancel\n5. Verify the row count is unchanged", "-")
    cal = open_calendar(case, page)
    baseline = cal.agenda_row_count()
    open_create_event(case, cal)
    case.click(cal.modal_multiple_events_tab, "'Multiple Events' tab")
    upload = wait_for_content(cal.multi_upload_label, timeout=10000)
    replace_label = cal.multi_replace_label.is_visible()
    unchecked = cal.multi_replace_checkbox.count() == 1 and not cal.multi_replace_checkbox.is_checked()
    template = cal.multi_template_link.is_visible()
    add = cal.multi_add_button.is_visible()
    single_hidden = cal.modal_title_input.count() == 0 or not cal.modal_title_input.is_visible()
    controls = upload and replace_label and unchecked and template and add and single_hidden
    case.check("Upload area, unchecked Replace option, template link and Add are shown; single-event fields are not",
               controls, expected="all present",
               actual=f"upload={upload}, replace={replace_label}, unchecked={unchecked}, template={template}, "
                      f"add={add}, single fields hidden={single_hidden}", locator=cal.multi_upload_label)
    case.click(cal.delete_cancel_button, "'Cancel' button")
    closed = cal.wait_modal_closed(10000)
    after = cal.agenda_row_count()
    ok = controls and closed and after == baseline
    case.check("Agenda is unchanged after Cancel", closed and after == baseline, expected=f"{baseline} rows",
               actual=f"closed={closed}, {after} rows")
    finish(case, result, ok, "Multiple Events tab showed its upload controls and Cancel changed nothing.",
           f"Multiple Events check failed: controls={controls}, closed={closed}, rows {baseline}->{after}.")


@pytest.mark.regression
def test_workspacecalendar_29_switching_tabs_restores_single_event_form(page, result):
    case = mk(page, "WorkspaceCalendar_29", FEATURE, "Switching back to Single Event restores the event form",
              "Going Single Event -> Multiple Events -> Single Event must bring back the Nature of Compliance, "
              "Description and Due Date fields and hide the upload area.",
              "1. Open Create New Event\n2. Multiple Events, then Single Event\n3. Verify the single-event fields",
              "-")
    cal = open_calendar(case, page)
    open_create_event(case, cal)
    case.click(cal.modal_multiple_events_tab, "'Multiple Events' tab")
    wait_for_content(cal.multi_upload_label, timeout=10000)
    case.click(cal.modal_single_event_tab, "'Single Event' tab")
    title = wait_for_content(cal.modal_title_input, timeout=10000)
    ok = title and cal.modal_description_input.is_visible() and cal.modal_due_date_input.is_visible() \
        and cal.multi_upload_label.count() == 0
    case.check("Single-event fields are back and the upload area is gone", ok, expected="fields visible, no upload",
               actual=f"title field={title}, upload labels={cal.multi_upload_label.count()}",
               locator=cal.modal_title_input)
    case.click(cal.delete_cancel_button, "'Cancel' button")
    finish(case, result, ok, "Single Event form was restored after switching tabs.",
           "Single Event form was not restored after switching tabs.")
