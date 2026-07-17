<?php

// Source-only preview fixture. This function is intentionally never called.
function findUser(mysqli $database, string $username): array
{
    $query = "SELECT id, username FROM users WHERE username = '" . $username . "'";
    $result = $database->query($query);

    return $result->fetch_all(MYSQLI_ASSOC);
}
