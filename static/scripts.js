function updateStatus(issueId, newStatus) {
  if (newStatus === 'under_process') {
    const form = document.getElementById(`update-form-${issueId}`);
    form.style.display = 'block';
    return; // Wait for user input before sending status
  }

  // For other statuses: directly update
  fetch(`/dashboard/update-status/${issueId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ status: newStatus })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      location.reload();
    } else {
      alert("Failed to update status.");
    }
  });
}

function submitUpdate(issueId) {
  const textarea = document.getElementById(`desc-${issueId}`);
  const updateText = textarea.value.trim();

  if (!updateText) {
    alert("Please enter a description before submitting.");
    return;
  }

  fetch(`/dashboard/update-description/${issueId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ description_update: updateText }) // Ensure key name matches Flask
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      location.reload();
    } else {
      alert("Failed to submit update: " + data.error);
    }
  })
  .catch(error => {
    console.error("Error:", error);
    alert("An error occurred while submitting the update.");
  });
}

