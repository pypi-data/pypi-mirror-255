import probablepeople as pp
import re


def filter_companies(name):

    """Take in a particular string and determine whether or not the string is a person using the probablepeople library
    Assert that
        1) ProbablePeople doesn't tag the name as a person OR
        2) the substring `|and|` is found in the name, which is much easier to parse as a company OR
        3) The name contains no spaces, which ProbablePeople likes to parse as a person AND
        4) The name does not start with a string, which these methods are poor at parsing right now"""

    # IMPORTANT: Cosine similarity (and really any fuzzy string match) doesn't work well on people
    # Think Smith, Tom A. and Smith, Tom B. -> are these people the same? A fuzzy string match would say yes. But can we be sure?
    # As such, for this its better to remove people from the output all together and deal with them later in the normalization process.
    # Fortunately the probablepeople library can be used to quickly identify strings that are people, and just ignore them.

    # Probable people performs poorly on bank names. Working to update training dataset but this is a quick fix for now

    try:
        val = pp.tag(name)
        return (
            (val[1] != "Person")
            or 'CorporationNameOrganization' in val[0]
            or 'CorporationNameBranchIdentifier' in val[0]
            or 'CorporationLegalType' in val[0]
            or ("|and|" in name)
            or (name.count(" ") == 0)
            or (re.search(" bank$", name))
            or 'citibank' in name
            or ("bennington crossing" in name)
        ) and not name[0].isdigit()
    except:
        return True


def filter_people(name):
    """Take in a particular string and determine whether or not the string is a person using the probablepeople library
    Assert that
        1) ProbablePeople tags the name as a person AND
        2) the substring `|and|` is not found in the name, which is much easier to parse as a company AND
        3) The name contains spaces (mononyms are often read as people by probablepeople. But more frequently refer to company names)
    """

    try:
        val = pp.tag(name)
        return (
            (val[1] == "Person")
            and 'CorporationNameOrganization' not in val[0]
            and 'CorporationNameBranchIdentifier' not in val[0]
            and 'CorporationLegalType' not in val[0]
            and 'citibank' not in name
            and ("|and|" not in name)
            and (name.count(" ") != 0)
            and not (re.search(" bank$", name))
            and ("bennington crossing" not in name)
        )
    except:
        return False
