/** @odoo-module **/
import { Chatter } from "@mail/components/chatter/chatter";
import { patch } from "web.utils";
import {onMounted, useState, onWillUnmount } from "@odoo/owl";



// Patch chatter 
patch(Chatter.prototype, "ep_chatter_search.Chatter.inherit", {

    setup() {
        this._super();
        this.state = useState({
            isSearchOpen: false,
            searchTerm: "",
            authors:[],
            activity_types:[],
            lastSelectedAuthor: 'All',
            lastSelectedActivity: 'All',
        });
        
        // Subscribe to the event
        onMounted(() => {
            this.env.bus.on('chatterTopbarButtonClicked', this, this.onClickSearch);        
        });
        
        onWillUnmount(() => {
            this.env.bus.off("chatterTopbarButtonClicked", this);
        });
    },

    onClickSearch() {
        // Toggle the boolean value
        this.state.isSearchOpen = !this.state.isSearchOpen;

    },

    onclickDropMenuAuthor(){
        const authorsSet = new Set();

        if (!this.props.record.thread || !this.props.record.thread.messages) {
            return;
        }
        for (const message of this.props.record.thread.messages) {

            authorsSet.add(message.author);

        }   
            this.state.authors = Array.from(authorsSet);
        
    },

    onclickDropMenuActivity(){
        const textSet = new Set();

        if (!this.props.record.thread || !this.props.record.thread.messages) {
            return;
        }
        for (const message of this.props.record.thread.messages) {
            var tempDiv = document.createElement('div');
            tempDiv.innerHTML = message.body;
    
            var spanElements = tempDiv.getElementsByTagName('span');
    
            for (let i = 1; i < spanElements.length; i += 2) {
                const iconSpan = spanElements[i - 1];
                const textSpan = spanElements[i];
    
                if (iconSpan.classList.contains('fa')) {
                    const extractedText = textSpan.textContent.trim();
                    textSet.add(extractedText);
                }
            }
        }
    
        this.state.activity_types = Array.from(textSet);
    },

    closeSearch() {
        this.state.isSearchOpen = false;
    },

    filterMessagesByAuthorAndActivity(author,activity) {

        const separators = document.querySelectorAll('.o_MessageList_separator');
        const authorDropdown = document.querySelector('.authorDropdown');
        const activityDropdown = document.querySelector('.activityDropdown');

        if (author == 'All' || author == '') {
            authorDropdown.textContent = 'Tous les utilisateurs';}
        else{
            authorDropdown.textContent = author;
            }
        if (activity == 'All' || activity == '') {
            activityDropdown.textContent = 'Toutes les activités';}
        else{
            activityDropdown.textContent = activity;
            }
        this.state.lastSelectedAuthor = author;
        this.state.lastSelectedActivity = activity;

        // Iterate over each separator
        separators.forEach(separator => {
            // Get the next sibling of the separator
            let nextMessage = separator.nextElementSibling;

            // Flag to check if any message is found after the separator
            let messageFound = false;

            // Check if the next sibling is a message
            while (nextMessage && nextMessage.classList.contains('o_Message')) {
                const messageText = nextMessage.textContent.trim();
                const authorElement = nextMessage.querySelector('.o_Message_authorName');
                const messageAuthor = authorElement.textContent.trim();
                // Check if messageText contains author / activity
                const isMatch = (author === 'All' || messageAuthor.includes(author)) &&
                            (activity === 'All' || messageText.includes(activity));

                // Hide the message if it doesn't contain the search term
                if (!isMatch) {
                    nextMessage.hidden = true;
                } else {
                    nextMessage.hidden = false; // Show the message if it matches
                    messageFound = true;                        
                }

                // Move to the next message
                nextMessage = nextMessage.nextElementSibling;
            }

            // Hide the separator if there are no messages after it
            separator.style.setProperty('display', messageFound ? '' : 'none', 'important');
        });
    
      },
    
    
    /** @param {KeyboardEvent} ev */
    onKeyupSearch(ev) {
            // Get all message separators
            const separators = document.querySelectorAll('.o_MessageList_separator');
            this.state.searchTerm = ev.target.value.trim().toLowerCase(); // Update the searchTerm state

            // Iterate over each separator
            separators.forEach(separator => {
                // Get the next sibling of the separator
                let nextMessage = separator.nextElementSibling;

                // Flag to check if any message is found after the separator
                let messageFound = false;

                // Check if the next sibling is a message
                while (nextMessage && nextMessage.classList.contains('o_Message')) {
                    // Check if the message text content contains the search term
                    const messageText = nextMessage.textContent.trim().toLowerCase();
                    const isMatch = messageText.includes(this.state.searchTerm);


                    // Hide the message if it doesn't contain the search term
                    if (!isMatch) {
                        nextMessage.hidden = true;
                    } else {
                        nextMessage.hidden = false; // Show the message if it matches
                        messageFound = true;                        
                    }

                    // Move to the next message
                    nextMessage = nextMessage.nextElementSibling;
                }

                // Hide the separator if there are no messages after it
                separator.style.setProperty('display', messageFound ? '' : 'none', 'important');
            });
            }


});


