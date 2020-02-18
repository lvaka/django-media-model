from django.db import models
from PIL import Image
import os, random, hashlib
from django.core.files.base import ContentFile
from io import BytesIO

# Create your models here.
class Media(models.Model):
	"""
		Media model. Should save image and create 
		multiple resized images if media is an image
	"""
	alt = models.CharField(max_length=160, null=False, blank=False)
	media_format = models.CharField(max_length=50, null=True, blank=True)
	full = models.FileField(upload_to='%Y/%m')
	preview = models.ImageField(upload_to='%Y/%m', null=True, blank=True)
	small = models.ImageField(upload_to='%Y/%m', null=True, blank=True)
	medium = models.ImageField(upload_to='%Y/%m', null=True, blank=True)
	large = models.ImageField(upload_to='%Y/%m', null=True, blank=True)

	
	def is_image(self):
		"""
			Checks image mimetype and 
			returns a bool whether or not 
			media is image or not.
		"""
		VALID_IMAGE_TYPES=(
			'image/jpeg',
			'image/png',
			'image/webp',
			'image/bmp',
		)

		mime_type = self.media_format
		return mime_type in VALID_IMAGE_TYPES

	
	def create_responsive_images(self, field):
		"""
			Generate responsive images from base image
		"""
		rand_hex = hashlib.md5(str(random.randint(0,1677215)).encode()).hexdigest()[:8]
		image = Image.open(field)
		path, ext = os.path.splitext(os.path.basename(field.path))
		width, height = image.size
		fullname = '%s%s%s'%(path, rand_hex, '.jpg')
		largename = '%s%s-%s%s'%(path, rand_hex, 'large', '.webp')
		mediumname = '%s%s-%s%s'%(path, rand_hex, 'medium', '.webp')
		smallname = '%s%s-%s%s'%(path, rand_hex, 'small', '.webp')

		def resize_image(image, re_width, file_format=None):
			"""
				Save full size image.  Only call 
				if uploaded image is larger than 1200px wide
			"""
			image_type = self.media_format

			size = (re_width, int(re_width * (height / width)))
			temp_image = image.resize(size, Image.ANTIALIAS)
			temp_file = BytesIO()
			temp_image.save(temp_file, file_format)
			temp_file.seek(0)
			file = ContentFile(temp_file.read())
			return file

		if width > 1200:
			file = resize_image(image, 1200, 'JPEG')
			self.full.save(fullname, file, save=False)

		else:
			file = resize_image(image, width, 'JPEG')
			self.full.save(fullname, file, save=False)

		if width > 992:
			file = resize_image(image, 992, 'WebP')
			self.large.save(largename, file, save=False)

		if width > 768:
			file = resize_image(image, 768, 'WebP')
			self.medium.save(mediumname, file, save=False)

		if width > 576:
			file = resize_image(image, 576, 'WebP')
			self.small.save(smallname, file, save=False)			


	def cleanup():
		"""
			Cleans up Files
		"""
		if os.path.isfile(self.full.path):
			os.remove(self.full.path)

		if self.preview and os.path.isfile(self.preview.path):
			os.remove(self.preview.path)

		if self.small and os.path.isfile(self.small.path):
			os.remove(self.small.path)

		if self.medium and os.path.isfile(self.medium.path):
			os.remove(self.medium.path)

		if self.large and os.path.isfile(self.large.path):
			os.remove(self.large.path)


	def save(self, *args, **kwargs):
		"""
			Should auto generate alt tag if none exists and 
			other image sizes
		"""
		previousData = Media.objects.get(pk=self.pk) if self.pk else None
		if not previousData or previousData.full != self.full:
			self.media_format = self.full.file.content_type
			if self.is_image():
				self.media_format = 'image/jpeg'
				self.create_responsive_images(self.full)

			elif self.preview:
				self.create_responsive_images(self.preview)

		if previousData and self.preview != previousData.preview:
			self.create_responsive_images(self.preview)			

		super(Media, self).save(*args, **kwargs)


	def delete(self, *args, **kwargs):
		"""
			Clean up files before delete.
			Does not clean up files that were changed 
			in between file creation and delete
		"""
		self.cleanup()

		super(Media, self).delete(*args, **kwargs)

	def __str__(self):
		return os.path.basename(self.full.name)

