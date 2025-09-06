$(document).ready(function() {
    const storeHours = [];
    for (let hour = 6; hour <= 17; hour++) {
        storeHours.push(hour);
    }
    const later = new tempusDominus.DateTime();
    later.days = 1;
    const hireFromPicker = $('#hire-from-picker').tempusDominus({
        allowInputToggle: true,
        display: {
            sideBySide: true,
            components: {
                calendar: true,
                date: true,
                month: true,
                year: true,
                decades: true,
                hours: true,
                minutes: true,
                seconds: false
            }
        },
        stepping: 30,
        restrictions: {
            minDate: new Date(),
            enabledHours: storeHours,
            disabledTimeIntervals: [
                { from: new tempusDominus.DateTime().startOf('date'), to: later }
            ]
        },
        localization: {
            hourCycle: "h24"
        }
    });

    const hireToPicker = $('#hire-to-picker').tempusDominus({
        allowInputToggle: true,
        display: {
            sideBySide: false,
            components: {
                calendar: true,
                date: true,
                month: true,
                year: true,
                decades: true,
                hours: true,
                minutes: true,
                seconds: false
            }
        },
        stepping: 30,
        restrictions: {
            minDate: new Date(),
            enabledHours: storeHours
        }
    });
});