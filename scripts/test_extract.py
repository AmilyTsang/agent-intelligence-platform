from app.tools import (
    company_search,
)

from app.tools.extract_tool import (
    extract_company_info,
)


def main():

    evidence = company_search.invoke(
        {
            "company": "OpenAI",
            "query": "Agent Tools definition"
        }
    )


    result = extract_company_info.invoke(
        {
            "company": "OpenAI",
            "topic": "Agent Tools",
            "evidence": evidence,
        }
    )


    print(result)


if __name__ == "__main__":
    main()