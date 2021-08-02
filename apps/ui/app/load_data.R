library(httr)
library(dplyr)
library(dotenv)

parse_datetime <- function(s) {
  return(s %>% str_replace("(\\d\\d):(\\d\\d)$", "\\1\\2") %>% str_replace("\\.\\d{6}", "") %>% as.POSIXct(format = "%Y-%m-%dT%H:%M:%S%z"))
}

load_dot_env()

# GET(url='http://localhost:5004/run')
# base_url <- "http://localhost:5002"

GET(url = paste0(Sys.getenv("COMPARATOR_SERVER"), "/run"))
base_url <- Sys.getenv("UI_BACKEND_SERVER")

req <- POST(url = paste0(base_url, "/token"), body = list(grant_type = "password", username = Sys.getenv("UI_BACKEND_USERNAME"), password = Sys.getenv("UI_BACKEND_PASSWORD")))
auth.token <- content(req)$access_token

req <- GET(paste0(base_url, "/recommendation/list"), add_headers("Authorization" = paste("Bearer", auth.token)))
recommendations <- jsonlite::fromJSON(content(req, as = "text", encoding = "UTF-8")) %>% as.data.frame()

req <- GET(paste0(base_url, "/patients/list"), add_headers("Authorization" = paste("Bearer", auth.token)))
patients <- jsonlite::fromJSON(content(req, as = "text", encoding = "UTF-8")) # %>% as.data.frame
patients$age <- floor(age_calc(as.Date(patients$birth_date), units = "years"))
patients$icu_day <- as.numeric(floor(age_calc(as.Date(patients$admission_hospitalisation), units = "days")))


load_recommendation_variables <- function(recommendation_id) {
  req <- GET(paste0(base_url, "/recommendation/variables/", recommendation_id), add_headers("Authorization" = paste("Bearer", auth.token)))
  recommendation_variables <- jsonlite::fromJSON(content(req, as = "text", encoding = "UTF-8"))
  return(recommendation_variables)
}

load_recommendation_results <- function(recommendation_id) {
  req <- GET(paste0(base_url, "/recommendation/get/", recommendation_id), add_headers("Authorization" = paste("Bearer", auth.token)))
  recommendation_results <- jsonlite::fromJSON(content(req, as = "text", encoding = "UTF-8"))
  gl_summary <- recommendation_results[["summary"]]
  gl_details <- recommendation_results[["detail"]]

  patient_results <- patients %>% inner_join(gl_summary, by = "pseudo_fallnr")
  return(patient_results)
}

load_patient <- function(patient_id, recommendation_id) {
  if (is.null(patient_id) | length(patient_id) == 0) {
    return(NULL)
  }
  # Use token to fetch the actual data.
  req <- GET(paste0(base_url, "/patient/get/?patient_id=", patient_id, "&recommendation_id=", recommendation_id), add_headers("Authorization" = paste("Bearer", auth.token)))
  patientdata <- jsonlite::fromJSON(content(req, as = "text", encoding = "UTF-8"))
  patientdata$datetime <- patientdata$datetime %>% parse_datetime()
  patientdata$datetime_end <- patientdata$datetime_end %>% parse_datetime()

  patientdata <- patientdata %>% arrange(variable_name, datetime)

  return(patientdata)
}
