$(document).ready(function() {
    var wordList = $(".word-list-container .word");
    wordList.each(function(index) {
        $(this).css("--index", index);
    });
});


    $(document).ready(function() {
        $('.add-to-watchlist').click(function(event) {
            event.preventDefault(); // Prevent the default form submission

            var artworkId = $(this).data('artwork-id');
            var nftId = $(this).data('nft-id');

            // Create an AJAX request to add the artwork to the watchlist
            $.ajax({
                type: 'POST',
                url: "{% url 'add_to_watchlist' %}",
                data: {
                    artwork_id: artworkId,
                    nft_id: nftId,
                    csrfmiddlewaretoken: '{{ csrf_token }}'
                },
                success: function(response) {
                    // Handle the success response here
                    console.log('Artwork added to watchlist successfully');
                },
                error: function(xhr, status, error) {
                    // Handle the error here
                    console.error('Error adding artwork to watchlist:', error);
                }
            });
        });
    });