import re
import mistune


def clean_response_text(text):
    """Cleans up the response text by removing any content inside 【 】 brackets and ensures proper punctuation spacing."""
    # print(f"Original response text:\n{text}", flush=True)

    # Remove anything inside 【 】, including the brackets themselves
    cleaned_text = re.sub(r"【[^】]*】", "", text)

    # Remove extra spaces before punctuation marks
    cleaned_text = re.sub(r"\s+([.,!?])", r"\1", cleaned_text)

    return cleaned_text.strip()


def convert_markdown_to_html(md_text):
    """Converts markdown text to HTML using mistune library."""
    markdown = mistune.create_markdown()
    html_content = markdown(md_text)

    # Hardcoding this case because this is a common pattern in email signatures and conversions don't handle it well
    # Check if the content ends with "Best regards, Defog AI Customer Support" and add a line break
    if "Best regards,\nDefog AI Customer Support" in html_content:
        html_content = re.sub(
            r"Best regards,\nDefog AI Customer Support",
            r"Best regards,<br>Defog AI Customer Support",
            html_content,
        )
    return html_content
