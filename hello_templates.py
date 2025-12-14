<!DOCTYPE html>
<html>
<head><title>Hello</title></head>
<body>
    <h1>Hello People</h1>
    <ul>
    {% for person in people %}
        <li>{{ person.name }}</li>
    {% empty %}
        <li>No people found.</li>
    {% endfor %}
    </ul>
</body>
</html>