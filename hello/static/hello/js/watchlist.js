$(document).ready(function() {
    $('.add-to-watchlist').click(function(event) {
      event.preventDefault(); // Prevent the default form submission
  
      var artworkId = $(this).data('artwork-id');
  
      // Create an AJAX request to add the artwork to the watchlist
      $.ajax({
        type: 'POST',
        url: "{% url 'add_to_watchlist' %}",
        data: {
          artwork_id: artworkId,
          csrfmiddlewaretoken: '{{ csrf_token }}'
        },
        success: function(response) {
          // Handle the success response here (e.g., display a success message)
          console.log('Artwork added to watchlist successfully');
        },
        error: function(xhr, status, error) {
          // Handle the error here (e.g., display an error message)
          console.error('Error adding artwork to watchlist:', error);
        }
      });
    });
  });
  