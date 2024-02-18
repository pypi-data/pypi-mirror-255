
from assertpy import assert_that
from netdot import gen_docs


def test_generate_markdown_API_docs(generate_docs):
    # Act
    docs = gen_docs.generate_markdown_docs()

    # ! SIDE EFFECT - Write updated documentation to file
    if generate_docs:
        with open('docs/generated-api-docs.md', 'w') as f:
            f.write(docs)

    # Assert
    assert_that(docs[:1000].lower()).contains('# netdot python api generated documentation')
    assert_that(docs).contains('add_device')


def test_generate_ENV_VARs_help_docs(generate_docs):
    # Act
    docs = gen_docs.generate_markdown_docs_ENV_VARs()

    # ! SIDE EFFECT - Write updated documentation to file
    if generate_docs:
        with open('docs/generated-env-var-docs.md', 'w') as f:
            f.write(docs)

    # Assert
    assert_that(docs).contains('NETDOT_CLI_TERSE')
    assert_that(docs).contains('SERVER_URL')
