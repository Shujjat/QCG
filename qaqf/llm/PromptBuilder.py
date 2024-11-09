import logging
from course_maker.models import LearningOutcome, ContentListing, Courses
from course_material.models import CourseMaterial

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class PromptBuilder:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def build_prolog(self, task_description, course_level):
        """
        Builds the prolog section of the prompt with general instructions.
        """
        prolog = f"""
        You are a highly skilled professor assigned to a task of course framework and content generation.
        The course level is SCQF Level {course_level} which means {self.get_scqf_level_info(course_level)}
        Your task is to {task_description}.
        Please ensure that your response is coherent and relevant.
        """
        return prolog

    def build_central(self, course):
        """
        Builds the central section of the prompt with course-specific data.
        """

        if course.long_course_support:
            duration = 6
        else:
            duration = course.duration
        central = f"""
        Course Details:
        - About Course: {course.course_description}
        - Course Type: {course.course_type}
        - Prerequisite Knowledge: {course.prerequisite_knowledge}
        - Learners Information: {course.participants_info}
        - language to use: {course.get_full_language_name(course.content_lang)}
        - should be optimized for Massive Open Online Course: {course.optimized_for_mooc}
        - should have a project at the end: {course.project_based}
        - course duration is: {duration}
        - practice intensity: {course.practice}
        """
        textbooks=CourseMaterial.objects.filter(course_id=course.id, material_type='textbook')
        helpingbooks=CourseMaterial.objects.filter(course_id=course.id, material_type='helpingbook')
        texts=""
        helpingtexts=""
        if textbooks.count()>0:
            texts = "Following is the main textbook content:"
            for textbook in textbooks:
                texts += "-------------------- Text Book Begins--------------------"
                texts += str(textbook.file_content)
                texts += "-------------------- Text Book Ends--------------------"

        if helpingbooks.count()>0:
            helpingtexts = "Following is the helping content:"
            for helpingbook in helpingbooks:
                helpingtexts += "-------------------- Helping Book Begins--------------------"
                helpingtexts += helpingbook.file_content
                helpingtexts += "-------------------- Helping Book Ends--------------------"

        if texts or helpingtexts:
            central += f"""
                        - Available Course Material to use as textbook or context is as under. It comprises textbooks and
                        helping books.
                        [Start of Material]
                        """
            if texts:
                central += texts

            if helpingtexts:
                central += helpingtexts

            central += f"""
                        [End of Course Material]
                       """
        else:
            central=""


        return central

    def build_epilog(self, output_format, course):
        """
        Builds the epilog section of the prompt, which includes formatting instructions for the response.
        """
        if output_format:

            epilog = f"""
            Please ensure the output is structured as follows:
            {output_format}
            """
        else:
            epilog=""
        return epilog

    def build_item_to_change(self, course, item_type, item_id=None):
        if item_type == "title":
            item_to_change = f"This title already exists and must be modified: {course.course_title}"
        elif item_type == "description":
            item_to_change = f"This description already exists and must be modified: {course.course_description}"
        elif item_id:
            if item_type == "learning_outcome":
                learning_outcome = LearningOutcome.objects.get(id=item_id)
                item_to_change = f"""
                                    This Learning outcome should be modified and improved: '{learning_outcome.outcome}'
                                    with sub items: '{learning_outcome.sub_items}'
                                """

            elif item_type == "content_listing":

                content_listing = ContentListing.objects.get(id=item_id)
                item_to_change = f"""
                                    This Content Listing should be modified and improved: '{content_listing.content_item}'
                                """
            else:
                item_to_change = ""

        else:
            item_to_change = ""
        return item_to_change

    def generate_measurement_level_prompt(self, level):
        """
        Generates a prompt based on the QAQF measurement level (1 to 9), integrating the QAQF Level Descriptors.
        Args:
            level (int): The level (1 to 9) representing the measurement stage.
        Returns:
            str: The generated prompt based on the provided level.
        """
        # Validate level
        if level not in range(1, 10):
            return ""

        # QAQF Characteristics
        characteristics = [
            "Knowledge and understanding",
            "Practice: Applied knowledge, skills and understanding",
            "Generic cognitive skills",
            "Communication and numeracy",
            "Autonomy, accountability and working with others",
            "Digitalisation, Artificial Intelligence, Advanced IT application, Robotics",
            "Reflective, creativity and Innovative skills",
            "Sustainability, resilience and ecological awareness",
            "Futuristic skills: futurology, genius, differentology"
        ]

        # Level Descriptors
        level_descriptors = {
            1: "Basic implementation of these characteristics",
            2: "Rudimentary implementation of these characteristics",
            3: "Crucial implementation of these characteristics",
            4: "Key implementation of these characteristics",
            5: "Substantial implementation of these characteristics",
            6: "Critical implementation of these characteristics",
            7: "Leading implementation of these characteristics",
            8: "Specialist implementation of these characteristics",
            9: "21st Century innovative and superior implementation of these characteristics"
        }

        # Guidelines
        guidelines = (
            "Level Descriptors provide a broad guide to what learners should be able to demonstrate at a given level. "
            "They offer a general overview and can assist with comparing qualifications and learning programs. "
            "The descriptors should be seen as a reference point, but not all characteristics need to be met for each qualification. "
            "It is important to assess across multiple levels to find the best fit. These descriptors can be used in creating program descriptions, "
            "learning outcomes, and assessment evidence."
        )

        # Construct the task description based on the level
        sub_prompt = (

            f"The assessment must evaluate the following nine characteristics:\n"
            f"{', '.join(characteristics)}.\n"
            f"The outcome of the assessment must demonstrate {level_descriptors[level]} to meet QAQF level {level} objectives.\n"
            f"{guidelines}"
        )

        return sub_prompt

    def build_full_prompt(self, task_description, course, output_format, item_type=None, item_id=None):

        """
        Combines the prolog, central, and epilog to create the full prompt.
        """

        prolog = self.build_prolog(task_description,course.course_level)
        central = self.build_central(course)
        epilog = self.build_epilog(output_format, course)

        if item_type:
            item_to_change = self.build_item_to_change(course, item_type, item_id)
        else:
            item_to_change = ""
        prompt = prolog + item_to_change + central + epilog
        logger.info(prompt)
        return prompt
    def get_course_material(self, course):
        """
        Builds the central section of the prompt with course-specific data.
        """

        course_material=""
        textbooks=CourseMaterial.objects.filter(course_id=course.id, material_type='textbook')
        helpingbooks=CourseMaterial.objects.filter(course_id=course.id, material_type='helpingbook')
        texts=""
        helpingtexts=""
        if textbooks.count()>0:
            texts = "Following is the main textbook content:"
            for textbook in textbooks:
                texts += "-------------------- Text Book Begins--------------------"
                texts += str(textbook.file_content)
                texts += "-------------------- Text Book Ends--------------------"

        if helpingbooks.count()>0:
            helpingtexts = "Following is the helping content:"
            for helpingbook in helpingbooks:
                helpingtexts += "-------------------- Helping Book Begins--------------------"
                helpingtexts += helpingbook.file_content
                helpingtexts += "-------------------- Helping Book Ends--------------------"

        if texts or helpingtexts:
            course_material += """
                        - Available Course Material to use as textbook or context is as under. It comprises textbooks and
                        helping books.
                        [Start of Material]
                        """
            if texts:
                course_material += texts

            if helpingtexts:
                course_material += helpingtexts

            course_material += f"""
                        [End of Course Material]
                       """
        else:
            course_material=""


        return course_material
    def get_scqf_level_info(self,level):
        scqf_qaqf_levels = {
            12: {
                "SCQF Qualification": "Doctoral Degree, Graduate Apprenticeship",
                "QAQF Benchmark": "21st Century Doctoral Degree",
                "Description": "Reflects an advanced capacity for independent research, critical thinking, and innovation."
            },
            11: {
                "SCQF Qualification": "Master's Degree, Integrated Master's Degree, Postgraduate Diploma/Certificate, Professional Apprenticeship",
                "QAQF Benchmark": "21st Century Master's Degree, Postgraduate Diploma, Graduate Certificate",
                "Description": "Emphasizes professional and high-level theoretical knowledge."
            },
            10: {
                "SCQF Qualification": "Honours Degree, Graduate Diploma/Certificate, SVQ Qualifications",
                "QAQF Benchmark": "Innovative Honours Degree, Graduate Certificate",
                "Description": "Promotes advanced knowledge and innovation within a specific field of study."
            },
            9: {
                "SCQF Qualification": "Professional Development Award, Bachelor's/Ordinary Degree, Graduate Apprenticeship",
                "QAQF Benchmark": "Creative Bachelor's/Ordinary Degree, Graduate Diploma",
                "Description": "Reflects a balanced blend of creative and practical skills."
            },
            8: {
                "SCQF Qualification": "Higher National Diploma, Diploma of Higher Education",
                "QAQF Benchmark": "Professional Diploma of Higher Education",
                "Description": "Supports a structured path for those entering professional or technical fields."
            },
            7: {
                "SCQF Qualification": "Advanced Higher, Scottish Baccalaureate, Higher National Certificate, Certificate of Higher Education",
                "QAQF Benchmark": "Resilient Certificate of Higher Education",
                "Description": "Promotes resilience and professional preparedness."
            },
            6: {
                "SCQF Qualification": "Higher, Skills for Work",
                "QAQF Benchmark": "Higher Apprenticeship",
                "Description": "Encourages applied knowledge and work-readiness in technical fields."
            },
            5: {
                "SCQF Qualification": "National 5",
                "QAQF Benchmark": "Technical Apprenticeship",
                "Description": "Suitable for those gaining initial exposure to technical work settings."
            },
            4: {
                "SCQF Qualification": "National 4, National Certificates",
                "QAQF Benchmark": "Basic Professional Qualification",
                "Description": "Foundational level promoting early skill development."
            },
            3: {
                "SCQF Qualification": "National 3",
                "QAQF Benchmark": "Basic Professional Qualification",
                "Description": "Early skill development level, building foundational competencies."
            },
            2: {
                "SCQF Qualification": "National 2",
                "QAQF Benchmark": "Foundational Learning",
                "Description": "Basic level for foundational skill-building."
            },
            1: {
                "SCQF Qualification": "National 1",
                "QAQF Benchmark": "Introductory Learning",
                "Description": "Introductory level supporting initial learning and skill acquisition."
            }
        }

        level_info = scqf_qaqf_levels.get(level)

        if not level_info:
            return "Level information not found."

        # Format the level information into a humanized paragraph
        return (
            f"SCQF Level {level} corresponds to qualifications such as {level_info['SCQF Qualification']}. "
            f"In terms of the QAQF Benchmark, it aligns with the \"{level_info['QAQF Benchmark']}.\" "
            f"This level is characterized as {level_info['Description']}"
        )
