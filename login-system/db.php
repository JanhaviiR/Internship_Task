<?php
$host = "localhost";
$user = "root";
$pass = "";
$db = "user_auth";

$conn = new mysqli($host, $user, $pass, $db);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Set charset to utf8mb4 for proper encoding
$conn->set_charset("utf8mb4");
?>