"""
Build Gmail search queries that surface candidate account-related emails.

We deliberately search narrowly (keyword/subject based) rather than pulling
the entire inbox - this keeps both the API usage and the amount of data we
ever see to a minimum, in line with the "don't send unnecessary data"
principle applied throughout this project.
"""

# Each tuple is (search_query_fragment, evidence_type_hint) used to build
# both the Gmail query and a hint for the rule engine about what the match
# probably represents.
CANDIDATE_SEARCH_TERMS: list[tuple[str, str]] = [
    ('subject:(verify your email OR "confirm your email" OR "confirm your account")', "account_verification"),
    ('subject:("welcome to" OR "welcome aboard" OR "your account is ready")', "welcome_email"),
    ('subject:("reset your password" OR "password reset" OR "reset password")', "password_reset"),
    ('subject:("new sign-in" OR "security alert" OR "unusual sign-in activity")', "security_notice"),
    ('subject:("your order" OR "order confirmation" OR "your receipt")', "purchase_receipt"),
    ('subject:("account created" OR "your new account")', "account_verification"),
]

# Exclude obvious noise up front (marketing blasts, social notifications that
# rarely indicate a distinct "account" worth surfacing).
EXCLUDED_LABELS = ["category:promotions", "category:social"]


def build_candidate_queries() -> list[tuple[str, str]]:
    """
    Return a list of (gmail_query, evidence_type_hint) pairs.
    Running these as separate searches (rather than one giant OR) keeps each
    query fast and keeps the evidence_type hint attached to its results.
    """
    exclusion = " ".join(f"-{label}" for label in EXCLUDED_LABELS)
    return [(f"{query} {exclusion}", hint) for query, hint in CANDIDATE_SEARCH_TERMS]
