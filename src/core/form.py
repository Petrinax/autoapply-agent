import time
from typing import List, Optional

from pydantic import create_model
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select
from form_models import FormInput, TypeInput, SelectInput, Fieldset

from src.core.user import get_user_details
from src.core.logger import get_logger
logger = get_logger(__name__)


def get_form_data(driver: WebDriver) -> (List[FormInput], WebElement | None):
    dialog = driver.find_element(By.CSS_SELECTOR, "div[role='dialog']")
    try:
        form = dialog.find_element(By.TAG_NAME, "form")
    except NoSuchElementException as e:
        return list(), None, dialog
    # form_inputs = form.find_elements(By.CSS_SELECTOR, "input, textarea, select")
    fields = form.find_elements(By.CLASS_NAME, 'fb-dash-form-element')

    form_questions = []

    for field in fields:
        form_input = None
        if field.find_elements(By.TAG_NAME, 'fieldset'):
            # Fieldset present
            form_input = Fieldset(field)
        elif field.find_elements(By.TAG_NAME, 'select'):
            form_input = SelectInput(field)
        else:
            form_input = TypeInput(field)

        form_questions.append(form_input)

    return form_questions, form, dialog

"""
        input_id = input_field.get_attribute("id")
        # label = None

        # Try to find label using 'for' attribute
        if input_id:
            try:
                label = form.find_element(By.CSS_SELECTOR, f"label[for='{input_id}']").text
                form_input = FormInput(input_field, label)
                form_questions.append(form_input)
            except:
                print(f"No label found for input: {input_id}")
                logger.debug(f"No label found for input: {input_id}")
    return form_questions, form
"""



def get_next_button(form: WebElement) -> (bool, str, Optional[WebElement]):
    try:
        # Try to find and click the "Next" button
        next_button = form.find_element(By.CSS_SELECTOR, "button[aria-label='Continue to next step']")
        button_found = 'next'
        button_element = next_button
        # Wait for the page to update
    except NoSuchElementException:
        try:
            review_button = form.find_element(By.CSS_SELECTOR, "button[aria-label='Review your application']")
            button_found = 'review'
            button_element = review_button
        except NoSuchElementException:
            try:
                submit_button = form.find_element(By.CSS_SELECTOR, "button[aria-label='Submit application']")
                button_found = 'submit'
                button_element = submit_button
            except Exception as e:
                logger.debug(f"Error clicking 'Next/Review/Submit' button: {e}")
                return False, None, None
    return True, button_found, button_element


def fill_form_page(form_data: list[FormInput], form_element: WebElement):

    # field_response_formats: List[tuple[type(BaseModel), str]] = [(field.get_answer_format(), field.label) for field in form_data]

    response_fields = {f"question_{idx}": (field.get_answer_format(), ...) for idx, field in enumerate(form_data)}
    AnswerFormat = create_model('AnswerFormat', **response_fields)
    answers, status = get_user_details(AnswerFormat) if response_fields else ({}, None)

    for idx, field in enumerate(form_data):
        label = field.label
        input_element = field.element
        tag_name = field.tag_name
        # if tag_name == 'input' and input_element.get_attribute('value'):
        #     print(f"Skipping field {label}. pre-filled value: {input_element.get_attribute('value')}")
        #     continue
        # elif tag_name == 'select' and input_element.get_attribute('value').lower() != 'select an option':
        #     print(f"Skipping field {label}. pre-filled value: {input_element.get_attribute('value')}")
        #     continue
        if label and label.lower() != 'upload resume':
            # Use predefined user info or LLM to generate an answer
            # print("Manual Fill")

            ### AutoFill -------------------------------------------------------
            response = answers.get(f'question_{idx}')
            answer = response.get('answer')
            #
            if field.type == 'radio_fieldset':
                field: Fieldset = field
                matched = False
                for option in field.options:
                    if option.label.lower() == answer.lower():
                        option.label_element.click()
                        matched = True
                        break
                if not matched:
                    logger.debug(f"Could not select radio option '{answer}' for {label}")
            elif tag_name == "select":
                # Handle <select> fields
                select = Select(input_element)
                try:
                    select.select_by_visible_text(answer)  # Select by visible text
                except:
                    try:
                        select.select_by_value(answer)  # Select by value
                    except:
                        logger.debug(f"Could not select option '{answer}' for {label}")
            else:
                # Handle input and textarea fields
                input_element.clear()
                input_element.send_keys(answer)

            time.sleep(0.6)



