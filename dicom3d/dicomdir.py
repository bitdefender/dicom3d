import os
import pydicom
import numpy as np

class DiicomDir():
	def __init__(self):
		self.records = None
		self.all_studies = None
		self.all_series = None
		self.ignore_entries_without_pixel_spacing = True

	def _check_attributes(self, entity, attrs):

		# for each attribute
		for attr, value in attrs.items():

			# check if entity has the attribute
			v = getattr(entity, attr)
			if v is None:
				return False

			# check if values are identical
			if value != v:
				return False

		return True

	def find_records(self, attrs):
		""" finds records based on a dictionary of attributes """
		results = []

		for record in self.records:
			recordobj = record.get("record")		

			# filter records
			if attrs is not None and self._check_attributes(recordobj, attrs) == False: 
				continue
			results.append(record)

		return results

	def find_studies(self, records, attrs):
		""" finds studies based on a dictionary of attributes, from a list of given records """
		results = []

		for record in records:
			for study in record.get("studies"):

				# filter studies
				studyobj = study.get("study")
				if attrs is not None and self._check_attributes(studyobj, attrs) == False: 
					continue

				results.append(study)

		return results

	def find_series(self, studies, attrs):
		""" finds series based on a dictionary of attributes, from a list of given studies """
		results = []

		for study in studies:
			for series in study.get("series"):

				# filter series
				seriesobj = series.get("series")
				if attrs is not None and self._check_attributes(seriesobj, attrs) == False:
					continue
				results.append(series)

		return results


	def find(self, record_attrs=None, study_attrs=None, series_attrs=None):
		""" finds records, studies and series based on a set of given attributes for each """

		if record_attrs is not None:
			records = self.find_records(record_attrs)
			if len(records) == 0:
				return []
		else:
			records = list(self.records)

		if study_attrs is not None:
			studies = self.find_studies(records, study_attrs)
			if len(studies) == 0: 
				return []
		else:
			studies = list(self.all_studies)

		if series_attrs is not None:
			series = self.find_series(studies, series_attrs)
			if len(series) == 0:
				return []
		else:
			series = list(self.all_series)

		return (records, studies, series)

	def load(self, filepath):
		""" loads a dicomdir from a given filepath """

		# check if file exists
		if not os.path.exists(filepath):
			raise ValueError("Inexistent filepath: " + filepath) 

		dicom_dir = pydicom.filereader.read_dicomdir(filepath)
		base_dir = os.path.dirname(filepath)

		records = []

		# go through the patient record and print information
		for patient_record in dicom_dir.patient_records:

			# add new record
			record_studies = []
			record_entry = {
				"patient_id"   : patient_record.PatientID   if hasattr(patient_record, "PatientID") else "N/A",
				"patient_name" : patient_record.PatientName if hasattr(patient_record, "PatientName") else "N/A",
				"studies"      : record_studies,
				"record"	   : patient_record
			}
			records.append(record_entry)

			# for each stufy
			studies = patient_record.children
			for study in studies:
				
				# add new study
				study_series = []
				study_entry = {
					"id"     : study.StudyID          if hasattr(study, "StudyID") else "N/A",
					"date"   : study.StudyDate        if hasattr(study, "StudyDate") else "N/A",
					"desc"   : study.StudyDescription if hasattr(study, "StudyDescription") else "N/A",
					"series" : study_series,
					"study"  : study
				}
				record_studies.append(study_entry)

				all_series = study.children

				# go through each series
				for series in all_series:
					image_count = len(series.children)
					
					# Put N/A in if no Series Description
					if 'SeriesDescription' not in series:
						series.SeriesDescription = "N/A"

					# add new series
					series_datasets = []
					series_entry = {
						"number"  : series.SeriesNumber      if hasattr(series, "SeriesNumber") else "N/A",
						"desc"    : series.SeriesDescription if hasattr(series, "SeriesDescription") else "N/A",
						"modality": series.Modality          if hasattr(series, "Modality") else "N/A",
						"images_count": image_count,
						"datasets" : series_datasets,
						"series"   : series
					}
					study_series.append(series_entry)

					# open and read each dataset
					image_records = series.children
					image_filenames = [os.path.join(base_dir, *image_rec.ReferencedFileID)
									   for image_rec in image_records]

					datasets = [pydicom.dcmread(image_filename)
								for image_filename in image_filenames]

					series_datasets.extend(datasets)

					# Don't load series with datasets that have no pixel spacing
					if self.ignore_entries_without_pixel_spacing:
						if hasattr(datasets[0],"PixelSpacing") == False:
							print("warning: ignoring series '%s' (%s) because datasets have no PixelSpacing attribute" % (
								series_entry.get("number"), series_entry.get("desc")) )
							study_series.remove(series_entry)


		self.records 	= records
		self.all_studies = self.find_studies(self.records, None) 
		self.all_series  = self.find_series (self.all_studies, None)

		return

	def print(self):
		""" Prints loaded records, studies and series"""

		if self.records is None:
			print("No records loaded.")
			return

		for ir, record in enumerate(self.records):
			id, name = record.get("patient_id"), record.get("patient_name")
			print("[%d] Name: %s (%s)" % (ir, name, id))

			for ist, study in enumerate(record.get("studies")):
				id, desc = study.get("id"), study.get("desc")
				print("-"*2 + "[%d] Id: %s Desc: %s" % (ist, id, desc))

				for ise, series in enumerate(study.get("series")):
					number, desc, imc = series.get("number"), series.get("desc"), series.get("images_count")
					print("-"*4 + "[%d] Number: %s Desc: %s Images: %d" % (ise, number, desc, imc))



	