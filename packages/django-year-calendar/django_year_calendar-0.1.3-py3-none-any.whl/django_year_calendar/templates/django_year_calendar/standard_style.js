    style: 'custom',

    customDataSourceRenderer: function (elt, currentDate, events) {
	// code from https://github.com/year-calendar/js-year-calendar/blob/master/src/ts/js-year-calendar.ts
	// rev 446cf94
	// helper for building custom renderers; this one is a dummy custom renderer cloning the standard one
	// USEFUL FOR TESTS ONLY
	// protected _renderDataSourceDay(elt: HTMLElement, currentDate: Date, events: T[]): void {
		const parent = elt.parentElement;

		switch (this.options.style)
		{
			case 'border':
				var weight = 0;

				if (events.length == 1) {
					weight = 4;
				}
				else if (events.length <= 3) {
					weight = 2;
				}
				else {
					parent.style.boxShadow = 'inset 0 -4px 0 0 black';
				}

				if (weight > 0)
				{
					var boxShadow = '';

					for (var i = 0; i < events.length; i++)
					{
						if (boxShadow != '') {
							boxShadow += ",";
						}

						boxShadow += `inset 0 -${(i + 1) * weight}px 0 0 ${events[i].color}`;
					}

					parent.style.boxShadow = boxShadow;
				}
				break;

			case 'background':
				parent.style.backgroundColor = events[events.length - 1].color;

				var currentTime = currentDate.getTime();

				if (events[events.length - 1].startDate.getTime() == currentTime)
				{
					parent.classList.add('day-start');

					if (events[events.length - 1].startHalfDay || this.options.alwaysHalfDay) {
						parent.classList.add('day-half');

						// Find color for other half
						var otherColor = 'transparent';
						for (var i = events.length - 2; i >= 0; i--) {
							if (events[i].startDate.getTime() != currentTime || (!events[i].startHalfDay && !this.options.alwaysHalfDay)) {
								otherColor = events[i].color;
								break;
							}
						}

						parent.style.background = `linear-gradient(-45deg, ${events[events.length - 1].color}, ${events[events.length - 1].color} 49%, ${otherColor} 51%, ${otherColor})`;
					}
					else if (this.options.roundRangeLimits) {
						parent.classList.add('round-left');
					}
				}
				else if (events[events.length - 1].endDate.getTime() == currentTime)
				{
					parent.classList.add('day-end');

					if (events[events.length - 1].endHalfDay || this.options.alwaysHalfDay) {
						parent.classList.add('day-half');

						// Find color for other half
						var otherColor = 'transparent';
						for (var i = events.length - 2; i >= 0; i--) {
							if (events[i].endDate.getTime() != currentTime || (!events[i].endHalfDay &&  !this.options.alwaysHalfDay)) {
								otherColor = events[i].color;
								break;
							}
						}

						parent.style.background = `linear-gradient(135deg, ${events[events.length - 1].color}, ${events[events.length - 1].color} 49%, ${otherColor} 51%, ${otherColor})`;
					}
					else if (this.options.roundRangeLimits) {
						parent.classList.add('round-right');
					}
				}
				break;

			//case 'custom':
			//	if (this.options.customDataSourceRenderer) {
		    //			this.options.customDataSourceRenderer.call(this, elt, currentDate, events);
			//	}
			//	break;
		}
	}
