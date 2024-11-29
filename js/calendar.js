const popup = document.getElementById('popup');
const delBtn = document.getElementById('deleteBtn');
const closeBtn = document.getElementById('closeBtn');
const todayEvents = document.getElementById('todayEvents');

const title = document.getElementById('event-title');
const startTime = document.getElementById('event-startTime');
const endTime = document.getElementById('event-endTime');
const reminder = document.getElementById('checkbox');

let curEvent = '';
let curReminder = false;

const req = new XMLHttpRequest();

document.addEventListener('DOMContentLoaded', async function() {
    var calendarEl = document.getElementById('calendar');
    const response = await fetch('/database');
    const data = await response.json();

    const eventList = [];
    data.forEach(function(msg) {
        eventList.push({title: msg.title, start: msg.startTime, end: msg.endTime, extendedProps: {id: msg._id}});
    });

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
            reminder.checked = info.event.extendedProps.reminder;
            title.innerHTML = info.event.title;
            startTime.innerHTML = new Date(info.event.start).toLocaleString();
            if (info.event.end != '') endTime.innerHTML = new Date(info.event.start).toLocaleString();
            curEvent = info.event;

            info.el.parentNode.appendChild(popup);
            popup.style.display = 'inline-block';
        },
        eventChange: function(info) {
            req.open('POST', '/event/'+info.event.extendedProps.id+'/edit', true)
            req.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
            req.send('startTime='+info.event.start+'&endTime='+info.event.end);
        },

    });
    calendar.render();
}); 

delBtn.addEventListener('click', function() {
    req.open('POST', '/event/'+curEvent.extendedProps.id+'/delete', true)
    req.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
    req.send();   
    curEvent.remove();
    popup.style.display = 'none';

    // update today's events list
    for (let i=0; i < todayEvents.childNodes.length; i++) {
        const id = todayEvents.childNodes[i].childNodes[1];
        if (id != undefined && id.value == curEvent.extendedProps.id) {
            todayEvents.removeChild(todayEvents.childNodes[i]);
        }
    }
});

closeBtn.addEventListener('click', function() {
    popup.style.display = 'none' ;
    curEvent.setExtendedProp('reminder', reminder.checked);
    req.open('POST', '/event/'+curEvent.extendedProps.id+'/edit', true)
    req.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
    req.send('reminder='+reminder.checked);       
});