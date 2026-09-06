from app.tools.search_tool import company_search
from app.tools.extract_tool import extract_company_info
from app.tools.comparison_tool import compare_companies


def main():

    openai_evidence = company_search.invoke(
        {
            "company": "OpenAI",
            "query": "Agent Tools"
        }
    )


    google_evidence = company_search.invoke(
        {
            "company": "Google",
            "query": "Agent Tools"
        }
    )


    openai_info = extract_company_info.invoke(
        {
            "company": "OpenAI",
            "topic": "Agent Tools",
            "evidence": openai_evidence,
        }
    )


    google_info = extract_company_info.invoke(
        {
            "company": "Google",
            "topic": "Agent Tools",
            "evidence": google_evidence,
        }
    )


    result = compare_companies.invoke(
        {
            "company_a": "OpenAI",
            "company_a_info": str(openai_info),

            "company_b": "Google",
            "company_b_info": str(google_info),

            "topic": "Agent Tools",
        }
    )


    print(result)


if __name__ == "__main__":
    main()