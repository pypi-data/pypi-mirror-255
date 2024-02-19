    enableRangeSelection: true,
    selectRange: function (e) {
		console.log(e);

		var data = '/';
		if (e.events.length > 0) {
			for (var i in e.events) {
			  if (e.events[i].ct == "") continue;
			  data += e.events[i].ct +':'+e.events[i].id + '&';
			}
			data = data.replace(/&$/, "/")
		}
		data += e.startDate.getTime()/1000 + '/'+ e.endDate.getTime()/1000

		const req = new Request('select' + data);
		fetch(req)
		  .then(response => response.text())
		  .then(result => {
			  const resultElement = document.querySelector('.modal-content');
			  resultElement.innerHTML = result;
		  });

		var myModal = new bootstrap.Modal(document.getElementById('myModal'), {
		  keyboard: false });
		myModal.show();
    },
