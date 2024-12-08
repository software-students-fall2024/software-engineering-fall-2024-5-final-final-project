let curEvent = '';
const req = new XMLHttpRequest();

document.addEventListener('DOMContentLoaded', async function() {
    var calendarEl = document.getElementById('calendar');
    const response = await fetch('/database');
    const data = JSON.parse(await response.json());

    const eventList = [];
    data.forEach(function(msg) {
        console.log(typeof msg.time)
        eventList.push({title: msg.name, start: msg.time, extendedProps: {id: msg._id}});
    });

    console.log(eventList)

    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        events: eventList,
        editable: true,
        dayMaxEvents: true,
        eventClick: function(info) {
            window.location.href = 'http://localhost:3000/event/' +  info.event.extendedProps.id.$oid+'/edit';
        },
        eventChange: function(info) {
            req.open('POST', '/event/'+info.event.extendedProps.id.$oid+'/time', true)
            req.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
            console.log(info.event.start.toISOString())

            req.send(`start=${encodeURIComponent(info.event.start.toISOString())}`);
        },
        eventDurationEditable: false,
    });
    calendar.render();
}); 