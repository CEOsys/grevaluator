library(httr)

## ANFANG ########### Neuer Part
# run once
# GET(url='http://localhost:5004/run')

base_url <- "http://localhost:5002"

req <- POST(url = paste0(base_url, "/token"), body = list(grant_type = "password", username = "tbienert", password = "lins3sefls3ke1q2:s3rfsd"))
auth.token <- content(req)$access_token

# Use token to fetch the actual data.
req <- GET(paste0(base_url, "/guideline/list"), add_headers("Authorization" = paste("Bearer", auth.token)))
guidelines <- jsonlite::fromJSON(content(req, as = "text", encoding = "UTF-8")) %>% as.data.frame()

req <- GET(paste0(base_url, "/patients/list"), add_headers("Authorization" = paste("Bearer", auth.token)))
patients <- jsonlite::fromJSON(content(req, as = "text", encoding = "UTF-8")) # %>% as.data.frame
patients$age <- floor(age_calc(as.Date(patients$birth_date), units = "years"))
patients$icu_day <- as.numeric(floor(age_calc(as.Date(patients$admission_hospitalisation), units = "days")))

patient_id <- patients$pseudo_fallnr[1]
guideline_id <- guidelines$id[1]

req <- GET(paste0(base_url, "/guideline/get/", guideline_id), add_headers("Authorization" = paste("Bearer", auth.token)))
guideline_results <- jsonlite::fromJSON(content(req, as = "text", encoding = "UTF-8"))
gl_summary <- guideline_results[["summary"]]
gl_details <- guideline_results[["detail"]]

patient_results <- patients %>% inner_join(gl_summary, by = "pseudo_fallnr")

# Use token to fetch the actual data.
req <- GET(paste0(base_url, "/patient/get/?patient_id=", patient_id, "&guideline_id=", guideline_id), add_headers("Authorization" = paste("Bearer", auth.token)))
patientdata <- jsonlite::fromJSON(content(req, as = "text", encoding = "UTF-8"))
