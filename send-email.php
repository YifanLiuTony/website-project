<?php
// Enable error reporting for debugging
error_reporting(E_ALL);
ini_set('display_errors', 0); // Don't display errors in response

// Set JSON header
header('Content-Type: application/json');

// Prevent direct access
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'Method not allowed']);
    exit;
}

try {
    // Get form data
    $name = isset($_POST['name']) ? htmlspecialchars($_POST['name']) : '';
    $email = isset($_POST['email']) ? htmlspecialchars($_POST['email']) : '';
    $phone = isset($_POST['phone']) ? htmlspecialchars($_POST['phone']) : '';
    $projectType = isset($_POST['projectType']) ? htmlspecialchars($_POST['projectType']) : '';
    $message = isset($_POST['message']) ? htmlspecialchars($_POST['message']) : '';

    // Validate required fields
    if (empty($name) || empty($email) || empty($phone) || empty($projectType) || empty($message)) {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => 'All fields are required']);
        exit;
    }

    // Validate email format
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => 'Invalid email address']);
        exit;
    }

    // Email configuration
    $to = 'info@sunfly.com.hk';
    $subject = 'New Contact Form Submission from ' . $name;

    // Email body (plain text)
    $body = "You have received a new contact form submission:\n\n";
    $body .= "Name: " . $name . "\n";
    $body .= "Email: " . $email . "\n";
    $body .= "Phone: " . $phone . "\n";
    $body .= "Project Type: " . $projectType . "\n\n";
    $body .= "Message:\n" . $message . "\n\n";
    $body .= "---\n";
    $body .= "This email was sent from the Sunfly Building Materials website contact form.";

    // Email headers
    $headers = "From: Sunfly Website <noreply@sunfly.com.hk>\r\n";
    $headers .= "Reply-To: " . $email . "\r\n";
    $headers .= "X-Mailer: PHP/" . phpversion() . "\r\n";
    $headers .= "Content-Type: text/plain; charset=UTF-8\r\n";

    // Try to send email
    // Note: mail() might not work on localhost without proper configuration
    $mailSent = @mail($to, $subject, $body, $headers);
    
    // Also save to file for testing purposes (so you can see the submissions even if mail fails)
    $logFile = 'email-logs.txt';
    $logEntry = "\n" . str_repeat("=", 50) . "\n";
    $logEntry .= "Date: " . date('Y-m-d H:i:s') . "\n";
    $logEntry .= "Name: " . $name . "\n";
    $logEntry .= "Email: " . $email . "\n";
    $logEntry .= "Phone: " . $phone . "\n";
    $logEntry .= "Project Type: " . $projectType . "\n";
    $logEntry .= "Message: " . $message . "\n";
    $logEntry .= str_repeat("=", 50) . "\n";
    
    file_put_contents($logFile, $logEntry, FILE_APPEND);

    // Return success (we consider it successful if it's logged, even if mail fails)
    http_response_code(200);
    echo json_encode([
        'success' => true,
        'message' => 'Message received successfully',
        'note' => $mailSent ? 'Email sent' : 'Email logged (mail server not configured)',
        'timestamp' => date('Y-m-d H:i:s')
    ]);

} catch (Exception $e) {
    // Handle any errors
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => 'Server error: ' . $e->getMessage()
    ]);
}
?>