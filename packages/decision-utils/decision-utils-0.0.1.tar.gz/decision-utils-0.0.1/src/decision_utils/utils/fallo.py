import re

regex = r"""\n
    (?=^\*+ # bold / italics at the start
        (
            (Where?fore)|
            (WHERE?FORE)|
            (WHEREFORE,\s+PREMISES\s+CONSIDERED)| # 65020
            (ACCORDINGLY)| # ACCORDINGLY examples, http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/63290; http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/64934
            (IN\s+
                (VIEW|LIGHT)\s+ # IN VIEW WHEREOF http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/33483; IN LIGHT OF ALL THE FOREGOING (46135)
                (
                    (W?HEREOF)| # IN VIEW HEREOF http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/33471
                    (THEREOF)| # IN VIEW THEREOF http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/34340
                    (
                        OF\s+
                        (ALL\s+)?
                        THE\s+
                        FOREGOING
                        (
                            \s+PREMISES|
                            \s+DISQUISITIONS?
                        )?
                    )| # IN VIEW OF ALL THE FOREGOING http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/64489
                    (OF\s+THESE\s+CONSIDERATIONS) # http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/33679
                )
            )|
            (
                (GIVEN\s+)?
                THE\s+FOREGOING\s+
                (
                    DISCOURSE|
                    PREMISES?|
                    DISQUISITIONS?
                )
                (\s+CONSIDERED)?
            )|
            (ON\s+ALL\s+THE\s+FOREGOING\s+CONSIDERATIONS)| # http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/33964
            (CONSIDERING\s+THE\s+FOREGOING)| # http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/33587, http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/34150, http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/34759
            (PREMISES CONSIDERED)| # http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/33729
            (FOR\s+
                (
                    THE\s+FOREGOING|
                    THESE|
                    THE\s+STATED
                )
                \s+
                REASONS
            )| # http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/33600
            (UPON\s+THESE\s+PREMISES) # http://elibrary.judiciary.gov.ph/thebookshelf/showdocsfriendly/1/34578
        )
        \,?
        \*+
        .*?
    )"""  # noqa: E501

pattern = re.compile(regex, re.X | re.M)


def add_fallo_comment(text: str):
    if not re.search(r"(<!--\s*##\s+Fallo\s*-->)", text):
        if len(pattern.findall(text)) == 1:
            return pattern.sub("\n\n<!-- ## Fallo -->\n", text)
    return text
