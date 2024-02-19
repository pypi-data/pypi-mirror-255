        enableRangeSelection: true,
        style: 'custom',
        allowOverlap: true,

        customDataSourceRenderer: function (elt, currentDate, events) {
{% comment %}

// this custom renderer allows to mix border and backgrouns style
// see helper standard_style.js to build your own custom renderer

{% endcomment %}
          var parent = elt.parentElement;
          var last = events.length - 1;
          if (events[last].own == 1) {
            parent.style.boxShadow = "inset 0 -4px 0 0 ".concat(events[last].color);
            if (last > 0 && events[last-1].own == 0) parent.style.backgroundColor = events[last-1].color;
          } else {
            parent.style.backgroundColor = events[last].color;
          }

          var currentTime = currentDate.getTime();

          if (events[last].startDate.getTime() == currentTime) {
            parent.classList.add('day-start');

            if (events[last].startHalfDay || this.options.alwaysHalfDay) {
              parent.classList.add('day-half'); // Find color for other half

              var otherColor = 'transparent';

              for (var i = events.length - 2; i >= 0; i--) {
                if (events[i].startDate.getTime() != currentTime || !events[i].startHalfDay && !this.options.alwaysHalfDay) {
                  otherColor = events[i].color;
                  break;
                }
              }

              parent.style.background = "linear-gradient(-45deg, ".concat(events[last].color, ", ").concat(events[last].color, " 49%, ").concat(otherColor, " 51%, ").concat(otherColor, ")");
            } else if (this.options.roundRangeLimits) {
              parent.classList.add('round-left');
            }
          } else if (events[last].endDate.getTime() == currentTime) {
            parent.classList.add('day-end');

            if (events[last].endHalfDay || this.options.alwaysHalfDay) {
              parent.classList.add('day-half'); // Find color for other half

              var otherColor = 'transparent';

              for (var i = events.length - 2; i >= 0; i--) {
                if (events[i].endDate.getTime() != currentTime || !events[i].endHalfDay && !this.options.alwaysHalfDay) {
                  otherColor = events[i].color;
                  break;
                }
              }

              parent.style.background = "linear-gradient(135deg, ".concat(events[last].color, ", ").concat(events[last].color, " 49%, ").concat(otherColor, " 51%, ").concat(otherColor, ")");
            } else if (this.options.roundRangeLimits) {
              parent.classList.add('round-right');
            }
          }

        },
