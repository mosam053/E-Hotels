$(document).ready(function() {
	$('#hotel-chain-filter').change(function() {
	  var selectedChain = $(this).val();
	  $.ajax({
		url: '/get_hotels',
		type: 'GET',
		data: {
		  chain: selectedChain
		},
		success: function(data) {
		  var hotelSelect = $('#hotel-filter');
		  hotelSelect.empty();
		  $.each(data.hotels, function(index, hotel) {
			hotelSelect.append($('<option>').text(hotel.locationName).attr('value', hotel.id));
		  });
		}
	  });
	});
  });