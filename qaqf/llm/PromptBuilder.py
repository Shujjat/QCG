import logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
from course_maker.models import LearningOutcome
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
    def build_item_to_change(self,item_type,item_id):
        if item_type == "learning_outcome":
            learning_outcome = LearningOutcome.objects.get(id=item_id)
            item_to_change = f"""
                                This Learning outcome should be modified and improved: '{learning_outcome}'
                            """
        elif item_type == "content_listing":
            learning_outcome = LearningOutcome.objects.get(id=item_id)
            item_to_change = f"""
                                This Content Listing should be modified and improved: '{learning_outcome}'
                            """
    def build_full_prompt(self, task_description, course, output_format,item_type=None,item_id=None):

        """
        Combines the prolog, central, and epilog to create the full prompt.
        """

        prolog = self.build_prolog(task_description)
        central = self.build_central(course)
        epilog = self.build_epilog(output_format)
        if item_id:
            item_to_change = self.build_item_to_change(item_type, item_id)
            return prolog + item_to_change + central + epilog
        else:
            return prolog  + central + epilog

