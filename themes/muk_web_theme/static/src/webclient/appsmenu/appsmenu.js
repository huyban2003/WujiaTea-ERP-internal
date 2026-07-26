import { onWillUnmount, useEffect } from "@odoo/owl";
import { user } from "@web/core/user";
import { url } from "@web/core/utils/urls";
import { useBus, useService } from "@web/core/utils/hooks";

import { Dropdown } from "@web/core/dropdown/dropdown";

// Set on <body> while the drawer is open, so the navbar can drop its
// background and app chrome (see appsmenu.scss) like the Enterprise home menu.
const BODY_CLASS = 'mk_apps_menu_open';

export class AppsMenu extends Dropdown {
    setup() {
    	super.setup();
    	this.commandPaletteOpen = false;
        this.commandService = useService("command");
    	if (user.activeCompany.has_background_image) {
            this.imageUrl = url('/web/image', {
                model: 'res.company',
                field: 'background_image',
                id: user.activeCompany.id,
            });
    	} else {
    		this.imageUrl = '/muk_web_theme/static/src/img/background.png';
    	}
        useEffect(
            (isOpen) => {
            	if (isOpen) {
            		const openMainPalette = (ev) => {
            	    	if (
            	    		!this.commandPaletteOpen &&
            	    		ev.key.length === 1 &&
            	    		!ev.ctrlKey &&
            	    		!ev.altKey
            	    	) {
	            	        this.commandService.openMainPalette(
            	        		{ searchValue: `/${ev.key}` }, 
            	        		() => { this.commandPaletteOpen = false; }
            	        	);
	            	    	this.commandPaletteOpen = true;
            	    	}
            		}
	            	window.addEventListener("keydown", openMainPalette);
	                return () => {
	                	window.removeEventListener("keydown", openMainPalette);
	                	this.commandPaletteOpen = false;
	                }
            	}
            },
            () => [this.state.isOpen]
		);
    	useBus(this.env.bus, "ACTION_MANAGER:UI-UPDATED", () => {
			if (this.state.isOpen) {
				this.state.close();
			}
		});
		onWillUnmount(() => document.body.classList.remove(BODY_CLASS));
    }
    onOpened() {
		super.onOpened();
		document.body.classList.add(BODY_CLASS);
		if (this.menuRef && this.menuRef.el) {
			this.menuRef.el.style.backgroundImage = `url('${this.imageUrl}')`;
		}
    }
    onClosed() {
		super.onClosed();
		document.body.classList.remove(BODY_CLASS);
    }
}
