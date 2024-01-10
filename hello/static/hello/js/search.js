// Fix ! Issue with crsf token

$(document).ready(function() {
    function resetSearchResults() {
        $(".result-container").empty();
    }

    // Function to handle search button click
    $(".search_btn").on("click", function() {
        resetSearchResults();
        var query = $("input[type='text']").val();
        if (query) {
            // Send AJAX request to the backend view
            var form_data = $("#search-form").serialize();
            // var formData = new FormData($("#search-form")[0]);

            $.ajax({
                url: "/search_req/",  // Replace with your backend view URL
                type: "POST",  // Change to "POST" if necessary
                data: { "query": query, "form_data":form_data, csrfmiddlewaretoken: '{{ csrf_token }}'},
                success: function(response) {
                    // Data received as JSON
                    console.log("Received data:", response);
                    console.log("form_data:",form_data)

                    var resultContainer = $(".result-container");
                    resultContainer.empty();  // Clear previous artwork data

                    console.log("made result container")
                    console.log("response.data:", response.length);

                    // Iterate through the data and create HTML elements for each artwork
                    for (var i = 0; i < response.length; i++) {
                        var result = response[i];
                        console.log('result', result.art_id)
                        var resultHTML = '<div class="result">';
                        if (result.art_id) {
                            // const imageDataUrl = `data:image/png;base64,${result.image_data}`;
                            console.log('image data:',result.image_data)
                            console.log(' art id :',result.art_id)
                            resultHTML += `
                                <h2>"${result.name}" - <a href="${result.is_for_sale ? result.art_details_url : result.sold_art_details_url}">Art Details</a>
                                </h2><img src="data:image/png;base64,${result.image_data}" alt="${result.name} Image">
                            `;
                        } else if (result.username) {
                            resultHTML += `
                                <h2>"${result.username}" - <a href="${result.public_profile_url}">User Profile</a></h2>
                            `;
                        } else if (result.nft_id) {
                            resultHTML += `
                            <h2>"${result.name}" -  <a href="${result.nft_details_url}">NFT Details</a></h2>
                            `;
                        }
                        resultHTML += '</div>';

                        resultContainer.append(resultHTML);
                        console.log("Generated HTML for result", i + 1, ":", resultHTML);
                    }
                }
            });
        }
    });

    // Handle changes in filter options and reset search results
    $("#time_frame, #min-price, #max-price, #sold, #for_sale, #want_artwork, #want_nfts").on("change", function() {
        resetSearchResults();
        var query = $("input[type='text']").val();
        if (query) {
            // Send AJAX request to the backend view
            var form_data = $("#search-form").serialize();
            // var formData = new FormData($("#search-form")[0]);

            $.ajax({
                url: "/search_req/",  // Replace with your backend view URL
                type: "POST",  // Change to "POST" if necessary
                data: { "query": query, "form_data":form_data, csrfmiddlewaretoken: '{{ csrf_token }}'},
                
                success: function(response) {
                    // Data received as JSON
                    console.log("Received data:", response);
                    console.log("form_data:",form_data)

                    var resultContainer = $(".result-container");
                    resultContainer.empty();  // Clear previous artwork data

                    console.log("made result container")
                    console.log("response.data:", response.length);

                    // Iterate through the data and create HTML elements for each artwork
                    for (var i = 0; i < response.length; i++) {
                        var result = response[i];
                        console.log('result', result)
                        var resultHTML = '<div class="result">';

                        if (result.art_id) {
                            resultHTML += `
                                <h2>"${result.name}" - <a href="${result.is_for_sale ? result.art_details_url : result.sold_art_details_url}">Art Details</a></h2>
                                <img src="data:image/png;base64,${result.image_data}" alt="${result.name} Image">
                            `;
                        } else if (result.username) {
                            resultHTML += `
                                <h2>"${result.username}" - <a href="${result.public_profile_url}">User Profile</a></h2>
                            `;
                        } else if (result.nft_id) {
                            resultHTML += `
                            <h2>"${result.name}" -  <a href="${result.nft_details_url}">NFT Details</a></h2>
                            `;
                        }
                        resultHTML += '</div>';


                        resultContainer.append(resultHTML);
                        console.log("Generated HTML for result", i + 1, ":", resultHTML);
                    }
                }
            });
        }
    });
});
