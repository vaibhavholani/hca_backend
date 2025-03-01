# Backend 
sudo launchctl unload /Library/LaunchDaemons/com.holani.cloth.agency.run.plist

# Frontend 
sudo launchctl unload /Library/LaunchDaemons/com.holani.cloth.agency.frontend.plist

# Backend
sudo launchctl load /Library/LaunchDaemons/com.holani.cloth.agency.run.plist

# Frontend 
sudo launchctl load /Library/LaunchDaemons/com.holani.cloth.agency.frontend.plist