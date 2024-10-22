# QAQFCourseGenerator (QCG)

This course generator uses Ollama local installation to complete its generative tasks.  
To install Ollama and run it locally, use the instructions available here:  
[https://github.com/ollama/ollama](https://github.com/ollama/ollama)

To run Ollama with LLAMA3, run this command:
Ollama run llama3



QCG is in initial development. Work on its 4th step is in progress. This is for sharing with our team for integration evaluation purposes.

Surely, there will be lots of issues and inconsistencies. They are deliberately left till the time once the complete flow is complete.

The QCG is being built using Django 5.1.1 with Python 3.12.

The REST framework is enabled.


--------

Here is the documentation-style endpoint breakdown for `api/regenerate/regenerate-items`:

---

### Endpoint: `GET /api/regenerate/regenerate-items`

This endpoint is used to regenerate course-related items such as the course title, description, learning outcomes, or content for a given course. It calls a Large Language Model (LLM) to regenerate the requested item.

---

### URL:
`/api/regenerate/regenerate-items`

### Method:
`GET`

### Parameters:

#### Required Query Parameters:
1. **course_id** (int):
   - **Description**: The unique identifier of the course for which the item is being regenerated.
   - **Example**: `course_id=1`

2. **item_type** (string):
   - **Description**: The type of item to regenerate. This can be one of the following:
     - **title**: Regenerates the course title.
     - **description**: Regenerates the course description.
     - **learning_outcome**: Regenerates the learning outcome(s) associated with the course.
     - **content**: Regenerates content listings for the course (e.g., quizzes, readings, videos).
   - **Example**: `item_type=title`, `item_type=learning_outcome`

3. **item_id** (int):
   - **Description**: The unique identifier of the specific item being regenerated. This is needed when regenerating learning outcomes or content.
   - **Example**: `item_id=5`

---

### Response:

#### Success:
- **Status**: `200 OK`
- **Body**: A JSON object containing the regenerated item for the specified `course_id` and `item_type`.

```json
{
  "regenerated_item (title)": "New AI Course Title"
}
```

#### Error:
- **Status**: `400 Bad Request`
- **Body**: A JSON object indicating the error, such as missing or invalid parameters.

```json
{
  "error": "Missing required fields: course_id, item_type"
}
```

---

### Example Request:

```http
GET /api/regenerate/regenerate-items?course_id=1&item_type=content&item_id=2
```

---

### Example Curl Request:

```bash
curl -X GET "http://127.0.0.1:8000/api/regenerate/regenerate-items?course_id=1&item_type=title"
```

---

### Notes:
- **Format options**: The endpoint can also accept an optional format parameter (e.g., `.json` or `.xml`) for specifying the response format if required.
   - **Example**: `/api/regenerate/regenerate-items.json?course_id=1&item_type=title`

- **item_type and item_id**:
  - **item_id** is not needed when regenerating the `title` or `description`, but is required for regenerating `learning_outcome` or `content`.
  
- The regeneration process interacts with a backend AI/LLM instance to generate content dynamically.
