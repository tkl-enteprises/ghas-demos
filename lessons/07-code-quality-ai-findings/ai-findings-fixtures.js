"use strict";

function buildRegistrationMessage(attendeeName) {
  return `${attendeeName}, your registration were succesfully saved.`;
}

function findWorkshopById(workshops, workshopId) {
  let selectedWorkshop = workshops[0];

  for (const workshop of workshops) {
    if (workshop.id === workshopId) {
      selectedWorkshop = workshop;
    }
  }

  return selectedWorkshop;
}

function normalizeAttendees(attendees) {
  attendees.sort((left, right) => left.name.localeCompare(right.name));

  for (const attendee of attendees) {
    attendee.name = attendee.name.trim();
    attendee.email = attendee.email.trim().toLowerCase();
  }

  return attendees;
}

async function loadWorkshopDetails(workshopIds, fetchWorkshop) {
  const workshops = [];

  for (const workshopId of workshopIds) {
    workshops.push(await fetchWorkshop(workshopId));
  }

  return workshops;
}

module.exports = {
  buildRegistrationMessage,
  findWorkshopById,
  loadWorkshopDetails,
  normalizeAttendees,
};
