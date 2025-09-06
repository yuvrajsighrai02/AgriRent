// ========== Initialise FullCalendar ==========
  document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
      initialView: 'dayGridMonth'
    });
    calendar.render();
  });

// ========== Fetch Events from API ==========
document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,timeGridDay'
      },
      initialView: 'dayGridMonth',
      navLinks: true,
      editable: true,
      dayMaxEvents: true,
      events: function(fetchInfo, successCallback, failureCallback) {
          fetch(`/api/equipment-returns?start=${fetchInfo.startStr}&end=${fetchInfo.endStr}`)
          .then(response => response.json())
          .then(events => successCallback(events))
          .catch(error => failureCallback(error));
      },
      eventClick: function(info) {
        var eventObj = info.event;
        var details = `
          <h4>Details</h4>
          <p><strong>Product:</strong> ${eventObj.title}</p>
          <p><strong>Customer:</strong> ${eventObj.extendedProps.customerName}</p>
          <p><strong>Email:</strong> ${eventObj.extendedProps.customerEmail}</p>
          <p><strong>Phone:</strong> ${eventObj.extendedProps.customerPhone}</p>
          <p><strong>Store:</strong> ${eventObj.extendedProps.storeName}</p>
          <p><strong>Address:</strong> ${eventObj.extendedProps.storeAddress}</p>
        `;

        // JavaScript to show modal with event details
        calendar.on('eventClick', function(info) {
          var eventObj = info.event;
          var modalBody = `
            <p><strong>Product:</strong> ${eventObj.title}</p>
            <p><strong>Customer:</strong> ${eventObj.extendedProps.customerName}</p>
            <p><strong>Email:</strong> ${eventObj.extendedProps.customerEmail}</p>
            <p><strong>Phone:</strong> ${eventObj.extendedProps.customerPhone}</p>
            <p><strong>Store:</strong> ${eventObj.extendedProps.storeName}</p>
            <p><strong>Address:</strong> ${eventObj.extendedProps.storeAddress}</p>
          `;
          $('#eventDetailsModal .modal-body').html(modalBody);
          $('#eventDetailsModal').modal('show');
        });
      }
    });
    calendar.render();
});





