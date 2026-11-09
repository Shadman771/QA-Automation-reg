"""Shared constants for TPA's "Tools" submenu (nested inside the unlabeled
"more" overflow menu alongside Treaties/Commentary/BEPS - see
pages/tpa/tpa_common.py::TpaNav.tools_submenu_toggle()).

Confirmed live via a full nav HTML dump (scratchpad discovery script, not
part of the suite): unlike WTA's own 2-item Tools dropdown (Projects,
Questionnaire Creator), TPA's "Tools" submenu holds exactly 4 real
children, each a direct `<a href="...">` link:

    Templates        -> /tpa/Templates
    Analyzer          -> /tpa/DecisionFlows   (on-page heading reads
                          "Please click the 'New Analysis' button to run
                          an Analysis." - the menu label "Analyzer" and
                          the route "DecisionFlows" intentionally differ,
                          confirmed live, not a mismatch to "fix")
    Projects          -> /tpa/Project
    FAR Questionnaire -> /tpa/FARQuestionnaireCreator

**Real, live-confirmed difference from WTA's own Tools pages**: every one
of these 4 TPA Tools pages supports a direct full-page deep link
(confirmed live for all 4 URLs - unlike WTA's Projects/Questionnaire
Creator, which redirect any direct `goto()` to /wta/Information) - so
every TPA Tools page object below has its own `goto()`, same pattern as
every other TPA page."""
TPA_TOOLS_SUBMENU_ITEMS = ["Templates", "Analyzer", "Projects", "FAR Questionnaire"]

TPA_TOOLS_ITEM_URLS = {
    "Templates": "/tpa/Templates",
    "Analyzer": "/tpa/DecisionFlows",
    "Projects": "/tpa/Project",
    "FAR Questionnaire": "/tpa/FARQuestionnaireCreator",
}
