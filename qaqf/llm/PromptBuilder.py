import logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
class PromptBuilder:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def build_prolog(self, task_description):
        """
        Builds the prolog section of the prompt with general instructions.
        """
        prolog = f"""
        You are a highly skilled assistant to a professor. Your task is to {task_description}.
        Please ensure that your response is coherent and relevant.
        """
        return prolog

    def build_central(self, course):
        """
        Builds the central section of the prompt with course-specific data.
        """
        central = f"""
        Course Details:
        - About Course: {course.course_description}
        - Course Type: {course.course_type}
        - Prerequisite Knowledge: {course.prerequisite_knowledge}
        - Learners Information: {course.participants_info}
        """

        if course.available_material_content:
            central += f"""
            - Available Study Material:
            [Start of Material]
            {course.available_material_content}
            [End of Material]
            """
        else:
            central += "\n- No additional study material available.\n"

        return central

    def build_epilog(self, output_format):
        """
        Builds the epilog section of the prompt, which includes formatting instructions for the response.
        """
        epilog = f"""
        Please ensure the output is structured as follows:
        {output_format}
        """
        return epilog

    def build_full_prompt(self, task_description, course, output_format):
        """
        Combines the prolog, central, and epilog to create the full prompt.
        """
        prolog = self.build_prolog(task_description)
        central = self.build_central(course)
        epilog = self.build_epilog(output_format)

        return prolog + central + epilog

