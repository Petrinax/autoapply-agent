from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Literal

from pydantic import BaseModel, Field
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class FormInput(ABC):
    # label: str
    # type: str
    # id: str
    # tag_name: str
    # name: str
    # element: WebElement
    """Represents a single form input field with its label and input element."""
    def __init__(self, element: WebElement):
        self.label: str | None = None
        self.type: str = element.get_attribute("type")
        self.id: str = element.get_attribute("id")
        self.tag_name: str = element.tag_name
        self.name: str = element.get_attribute("name")
        self.element: WebElement = element

    @abstractmethod
    def get_question(self) -> str:
        pass

    @abstractmethod
    def get_answer_format(self) -> type(BaseModel):
        pass


@dataclass
class RadioOption:
    label: str
    element: WebElement
    label_element: WebElement
    def __str__(self):
        return self.label

class Fieldset(FormInput):
    # .find_elements(By.CSS_SELECTOR, 'fieldset')[0]
    def __init__(self, field: WebElement):
        fieldset_element = field.find_element(By.TAG_NAME, 'fieldset')
        super().__init__(fieldset_element)
        self.type = 'radio_fieldset'
        radio_elements: List[WebElement] = fieldset_element.find_elements(By.CSS_SELECTOR, 'input')


        self.options: List[RadioOption] = []
        self.option_type = 'radio'
        self.label: str = fieldset_element.find_element(By.TAG_NAME, 'legend').text

        for radio_element in radio_elements:
            input_id = radio_element.get_attribute("id")
            inp_type = str(radio_element.get_attribute("type"))
            if inp_type != self.option_type:
                raise Exception(f"Unsupported Input Type: {inp_type} for Fieldset: {self.label}")
            label_element = fieldset_element.find_element(By.CSS_SELECTOR, f"label[for='{input_id}']")
            label = label_element.text
            option = RadioOption(label=label, element = radio_element, label_element=label_element)
            self.options.append(option)

        self.error_desc = ''
        error_desc_id = fieldset_element.get_attribute('aria-describedby')
        if field.find_elements(By.ID, error_desc_id):
            error_element = field.find_element(By.ID, error_desc_id)
            if error_element.find_elements(By.TAG_NAME, 'span'):
                self.error_desc = error_element.find_element(By.TAG_NAME, 'span').text

    def get_question(self) -> str:
        return self.label

    def get_answer_format(self):
        all_options = [str(option) for option in self.options]
        ques = self.label
        class FieldsetResponse(BaseModel):
            question: Literal[ques]
            answer: Literal[*all_options] = Field( description=f" Answer should be one of: {all_options}. {self.error_desc}")

        return FieldsetResponse


@dataclass
class SelectOption:
    label: str
    element: WebElement
    def __str__(self):
        return self.label


class SelectInput(FormInput):
    def __init__(self, field: WebElement):
        select_element = field.find_element(By.TAG_NAME, 'select')
        super().__init__(select_element)
        self.type = 'select_input'
        self.options : List[SelectOption] = []
        self.type = 'select'
        select_id = select_element.get_attribute("id")
        self.label: str = field.find_element(By.CSS_SELECTOR, f"label[for='{select_id}']").find_element(By.TAG_NAME, 'span').text

        for option_element in select_element.find_elements(By.TAG_NAME, 'option'):
            if 'select an option' not in option_element.text.lower():
                self.options.append(SelectOption(option_element.text, option_element))

        self.error_desc = ''
        error_desc_id = select_element.get_attribute('aria-describedby')
        if field.find_elements(By.ID, error_desc_id):
            error_element = field.find_element(By.ID, error_desc_id)
            if error_element.find_elements(By.TAG_NAME, 'span'):
                self.error_desc = error_element.find_element(By.TAG_NAME, 'span').text

    def get_question(self) -> str:
        return self.label

    def get_answer_format(self):
        all_options = [str(option) for option in self.options]
        ques = self.label
        class SelectInputResponse(BaseModel):
            question: Literal[ques]
            answer: Literal[*all_options] = Field( description=f" Answer should be one of: {all_options}. {self.error_desc}")

        return SelectInputResponse


class TypeInput(FormInput):
    def __init__(self, field: WebElement):

        input_element = field.find_element(By.TAG_NAME, 'input')
        super().__init__(input_element)
        self.type = 'type_input'
        self.type = input_element.get_attribute("type")
        input_id = input_element.get_attribute("id")
        self.label: str = field.find_element(By.CSS_SELECTOR, f"label[for='{input_id}']").text

        self.error_desc = ''
        error_desc_id = input_element.get_attribute('aria-describedby')
        if field.find_elements(By.ID, error_desc_id):
            error_element = field.find_element(By.ID, error_desc_id)
            if error_element.find_elements(By.TAG_NAME, 'span'):
                self.error_desc = error_element.find_element(By.TAG_NAME, 'span').text

    def get_question(self) -> str:
        return self.label

    def get_answer_format(self):
        # all_options = [str(option) for option in self.options]
        ques = self.label
        class TypeInputResponse(BaseModel):
            question: Literal[ques]
            answer: str = Field(description=f"{self.error_desc}")

        return TypeInputResponse

