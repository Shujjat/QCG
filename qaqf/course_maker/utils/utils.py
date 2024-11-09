from course_material.models import CourseMaterial
def get_course_material( course_id):
    """
    Builds the central section of the prompt with course-specific data.
    """

    course_material = ""
    textbooks = CourseMaterial.objects.filter(course_id=course_id, material_type='textbook')
    helpingbooks = CourseMaterial.objects.filter(course_id=course_id, material_type='helpingbook')
    texts = ""
    helpingtexts = ""
    if textbooks.count() > 0:
        texts = "Following is the main textbook content:"
        for textbook in textbooks:
            texts += "-------------------- Text Book Begins--------------------"
            texts += str(textbook.file_content)
            texts += "-------------------- Text Book Ends--------------------"

    if helpingbooks.count() > 0:
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
        course_material = ""

    return course_material