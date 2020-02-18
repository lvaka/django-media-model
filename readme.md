#Django 3.0 Media Manager Model
---

Requirements:  
Pillow 7.0.0  
Django 3.0  

REQUIRED FIELDS:  
Full  
Alt  
Full is the filed to upload media file to.  This can be an image or any other file type.  I made alt a required field as not having an alt tag negatively affects SEO.  So create alt tags for your media, people.

This is a simple app for django based media manager.  The model will automagically resize images or video previews into responsive WebP formats.  Full images are resized down to 1200 max width JPEGS.  I chose JPEG for the full width images to ensure decent file compression for web and for compatibility as not all browsers support WebP(though they really should).

Cleanup of files occurs during delete method of the model.  However, there is no clean up for when media files are updated or changed in between creation and deletion.  Best practice would be to delete media object from database if you are going to change the media file.  Reserve updates for changes to Alt Text.

No views or URL endpoints.  This allows flexibility to use it in a traditional MVC app or REST API. 
