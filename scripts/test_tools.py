from app.tools import company_search


def main():

    print(
        "\n========== OpenAI ==========\n"
    )

    result = company_search.invoke(
        {
            "company": "OpenAI",
            "query": (
                "What tools can AI agents use "
                "and how are tools defined?"
            )
        }
    )

    print(result)


if __name__ == "__main__":
    main()