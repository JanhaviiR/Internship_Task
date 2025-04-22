<?php
session_start();
if (!isset($_SESSION["user_id"])) {
    header("Location: login.php");
    exit();
}

include 'db.php';

// Get username
$stmt = $conn->prepare("SELECT username FROM users WHERE id = ?");
$stmt->bind_param("i", $_SESSION["user_id"]);
$stmt->execute();
$result = $stmt->get_result();
$user = $result->fetch_assoc();
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard | Auth System</title>
    <link rel="stylesheet" href="style.css">
    <style>
        .welcome-container {
            text-align: center;
            padding: 2rem;
        }
        
        .welcome-message {
            font-size: 2rem;
            margin-bottom: 2rem;
            color: var(--primary-color);
        }
        
        .logout-btn {
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: var(--border-radius);
            font-size: 1rem;
            cursor: pointer;
            transition: var(--transition);
            text-decoration: none;
            display: inline-block;
        }
        
        .logout-btn:hover {
            background-color: var(--secondary-color);
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="container welcome-container">
        <h1 class="welcome-message">Welcome, <?php echo htmlspecialchars($user['username']); ?>!</h1>
        <a href="logout.php" class="logout-btn">Logout</a>
    </div>
</body>
</html>