"use strict";

// These functions are inert workshop fixtures: they perform no I/O and are not
// invoked automatically. The two quality defects are intentional.
function buildGreeting(userName) {
  const preview = `Preview for ${userName}`;

  return {
    preview,
    message: "Welcome, ${userName}!",
  };
}

function countCompleted(tasks) {
  let completed = tasks.length;
  completed = tasks.filter((task) => task.complete).length;

  return completed;
}

module.exports = {
  buildGreeting,
  countCompleted,
};
