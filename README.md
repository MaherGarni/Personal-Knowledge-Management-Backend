Personal Knowledge Management App — Backend (Django)

This backend powers a personal knowledge-tracking system designed to help users organize their learning and skill development.
The system structures knowledge into three hierarchical levels: main topic → subtopic → skill, allowing users to add lessons for each skill and track progress over time.

The backend handles:
- User authentication & authorization
 
- Category and lesson CRUD operations
 
- Hierarchical data structure for skills
 
- AI-assisted validation and scoring for lessons

Skill-progress calculation and API responses consumed by the frontend

Each lesson created via the API is processed to ensure it belongs to the correct category and is scored based on depth and relevance. These scores are later used to display progress and skill level in the UI.

## Technology Used  

- **Django**   
- **Django REST Framework**   
- **PostgreSQL**    
- **Gemeni API**   
- **JWT Authentication**   
- **VS Code**   
- **GitHub**   

## Project Links  
- **[Frontend Repo](https://github.com/MaherGarni/Personal-Knowledge-Management-Frontend)**  
- **[Backend link](http://localhost:8000/)**  

## Routing Table 
<h3>User</h3>
<table border="1">
    <tr><th>HTTP Verb</th><th>Path</th><th>Action</th><th>Description</th></tr>
    <tr><td>POST</td><td>/users/signup</td><td>create</td><td>create new user</td></tr>
    <tr><td>POST</td><td>/users/login</td><td>authenticate</td><td>login a user</td></tr>
    <tr><td>POST</td><td>/users/tokens/refresh</td><td>update</td><td>Update user's refresh token</td></tr>
</table>


<h3>Category</h3>
<table border="1">
    <tr><th>HTTP Verb</th><th>Path</th><th>Action</th><th>Description</th></tr>
    <tr><td>GET</td><td>/categories</td><td>index</td><td>List all categories</td></tr>
    <tr><td>POST</td><td>/categories</td><td>create</td><td>create new category</td></tr>
    <tr><td>GET</td><td>/categories/:id</td><td>show</td><td>Show details of a category</td></tr>
    <tr><td>PUT</td><td>/categories/:id</td><td>update</td><td>Update a category</td></tr>
    <tr><td>DELETE</td><td>/categories/:id</td><td>delete</td><td>Delete a category</td></tr>
</table>

<h3>Lesson</h3>
<table border="1">
    <tr><th>HTTP Verb</th><th>Path</th><th>Action</th><th>Description</th></tr>
    <tr><td>GET</td><td>/categories/:id/lessons</td><td>index</td><td>List all lessons related to a category</td></tr>
    <tr><td>POST</td><td>/categories/:id/lessons</td><td>create</td><td>create new lesson in a category</td></tr>
    <tr><td>GET</td><td>/categories/:id/lessons/:id</td><td>show</td><td>Show details of a lesson</td></tr>
    <tr><td>PUT</td><td>/categories/:id/lessons/:id</td><td>update</td><td>Update a lesson</td></tr>
    <tr><td>DELETE</td><td>/categories/:id/lessons/:id</td><td>delete</td><td>Delete a lesson</td></tr>
</table>

<h3>SkillsLevels</h3>
<table border="1">
    <tr><th>HTTP Verb</th><th>Path</th><th>Action</th><th>Description</th></tr>
    <tr><td>GET</td><td>/skill_levels</td><td>index</td><td>List all skill levels</td></tr>
</table>

  
## Icebox Features  
- Support file/image uploads for lessons
- More advanced AI feedback + skill growth insights

