library(shiny)
library(ggplot2)
library(shinythemes)
library(DT)
library(eeptools)
library(stringr)
library(dplyr)
library(jsonlite)
library(httr)
library(purrr)
library(plotly)
library(glue)

source("load_data.R")
patient_id <- patients$pseudo_fallnr[1]
guideline_id <- guidelines$id[1]
# patient_results <- load_guideline_results(guideline_id)

variable_name_mappings <- list(
  test_covid19_pcr = "COVID19 PCR Test",
  body_position = "Lagerungsposition",
  ventilation_mode = "Beatmungsmodus",
  RASS = "RASS",
  drug_norepinephrine = "Katecholamine",
  drug_epinephrine = "Epinephrin",
  deltaSOFA = "ΔSOFA",
  drug_dobutamine = "Dobutamin",
  drug_dopamine = "Dopamin",
  oxygenation_index_calc = "Oxygenierungsindex",
  drug_vasopressin = "Vasopressin",
  sO2 = "sO2",
  respiratory_rate = "Atemfrequenz",
  drug_dexamethason_bolus = "Dexamethason"
)

ui <- fluidPage(
  # themeSelector(),
  theme = shinytheme("cerulean"),
  # tags$script(src = "absolute-sorting.js"),
  # tags$head(tags$script(src = "https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js", type = "text/javascript")),
  # tags$head(tags$script(src = "https://cdn.datatables.net/plug-ins/1.10.24/sorting/absolute.js", type = "text/javascript")),
  # tags$head(tags$script(HTML(  "var nameType = $.fn.dataTable.absoluteOrder( 'F00000092' );"))),
  # tags$head(tags$script(HTML(
  # "var numbersType = $.fn.dataTable.absoluteOrderNumber( [
  #  { value: 'N/A', position: 'bottom' }
  # ] );"
  # ))),
  tags$style(type = "text/css", "h1 { margin-top:0;} "),
  #*************************************************************************
  # Title Row

  fluidRow(
    column(4, selectInput(
      inputId = "ward", label = h3("Station"),
      choices = c("Alle"),
      selected = "Alle",
      width = "80%"
    ),
    align = "center"
    ),
    column(2, img(src = "logo_ceosys.jpg", height = 120), align = "right"),
    column(2, img(src = "logo_num.jpg", height = 120), align = "left"),
    column(4, selectInput(
      inputId = "guideline_id", label = h3("Leitlinie"),
      choices = setNames(guidelines$id, guidelines$title),
      selected = NULL,
      width = "80%"
    ),
    align = "center"
    )
  ),

  #*************************************************************************
  # Content Row

  fluidRow(

    # Patient Table Column

    column(
      5,
      wellPanel(
        h1("Patienten"),
        DT::dataTableOutput("patienttable")
      )
    ),

    # Guideline Column

    column(
      7,

      # Guideline-Text Row

      wellPanel(
        h1("Leitlinie"),
        htmlOutput("guideline_text"),
        tags$head(tags$style("#guideline_text { font-size:12px; max-height: 20%; }")),
      ),

      # Guideline-Population Row
      wellPanel(
        h1("Population"),
        uiOutput("population_main")
      ),

      # Guideline-Intervention Row
      wellPanel(
        h1("Intervention"),
        uiOutput("intervention_main")
      )
    )
  )
)

getPlotUIs <- function(vars, type) {
  return(renderUI({
    myTabs <- map(vars, ~ tabPanel(
      title = glue("{variable_name_mappings[.x]}"),
      wellPanel(
        plotlyOutput(paste("plot", type, .x, sep = "_"), height = 300),
        style = "padding:0;margin-bottom:0;"
      )
    ))

    do.call(tabsetPanel, myTabs)
  }))
}

setPlotUIOutputs <- function(output, patientdata, vars, type) {
  for (var in vars) {
    local({
      plotname <- paste("plot", type, var, sep = "_")
      localvar <- var

      output[[plotname]] <- renderPlotly({
        data <- patientdata() %>% filter(variable_name == localvar)
        data$value <- data$value %>% type.convert()
        max_dt <- max(patientdata()$datetime)

        if (nrow(data) == 0) {
          # no data
          ggp <- ggplot(data, aes(datetime, value)) +
            geom_blank() +
            expand_limits(x = c(max_dt - 86400 * 4, max_dt), y = c(0, 1))
        } else if (class(data$value) == "factor") {
          # categorical variables
          ggp <- ggplot(data, aes(x = datetime, y = value, group = value)) +
            geom_step(aes(group = 1)) +
            geom_point()
        } else if (any(!is.na(data$datetime_end))) {
          # time periods
          ggp <- ggplot(data, aes(y = value, yend = value, x = datetime, xend = datetime_end)) +
            geom_segment(size = 1)
        } else if (grepl("_bolus", localvar)) {
          # drug bolus
          ggp <- ggplot(data, aes(x = datetime, ymin = 0, y = value, ymax = value)) +
            geom_linerange() +
            geom_point()
        } else {
          # continuous data
          ggp <- ggplot(data, aes(datetime, value)) +
            geom_line() +
            geom_point()
        }
        ggplotly(ggp +
          xlab("Datum") +
          ylab(variable_name_mappings[[localvar]]) +
          coord_cartesian(xlim = c(max_dt - 86400 * 4, max_dt)))
      })
    })
  }
}

############# Server ############
server <- function(input, output, session) {
  tabldat <- reactive({
    if (input$ward == "Alle") {
      return(tabldspl())
    }
    else {
      return(tabldspl()[patient_results()$ward == input$ward, ])
    }
  })


  # Patient data table
  options(DT.options = list(pageLength = 20))
  observeEvent(input$ward, {
    output$patienttable <- DT::renderDataTable(
      server = FALSE,
      DT::datatable(tabldat(),
        rownames = FALSE,
        selection = list(mode = "single", selected = c(1)),
        colnames = c("Name", "Alter", "ITS-Tag ", "P", "I", "Leitlinienkonform"),
        options = list(
          columnDefs = list(
            list(
              render = JS(
                "function(data, type, row, meta) {",
                "if (type === 'display') {",
                "  if (data == true) {",
                "    return '&#10004;'",
                "  } else if (data == false) {",
                "    return '&#x2718;'",
                "  } else if (data == -1) {",
                "    return '';",
                "  }",
                "}",
                "return data",
                "}"
              ),
              className = "dt-center", targets = 1:5
            )
          )
        )
      ) %>% formatStyle(c(6),
        backgroundColor = styleEqual(
          c(TRUE, FALSE),
          c(
            rgb(200, 230, 200, 255, 255, 255),
            rgb(230, 200, 200, 255, 255, 255)
          )
        )
      )
    )
  })


  rv <- reactiveValues()
  rv$patient_id <- reactive({
    tabldat()[input$patienttable_rows_selected, ]$Name
  })
  rv$guideline_id <- reactive({
    input$guideline_id
  })



  ##### Functions for right column #####


  patientdata <- reactive({
    print("load patientdata")
    load_patient(rv$patient_id(), rv$guideline_id())
  })

  patient_results <- reactive({
    load_guideline_results(rv$guideline_id())
  })

  tabldspl <- reactive({
    t <- data.frame(
      "Name" = patient_results()$pseudo_fallnr,
      "Alter" = patient_results()$age,
      "ITSTag" = patient_results()$icu_day,
      "P" = patient_results()$valid_population,
      "I" = patient_results()$valid_exposure,
      "Leitlinienkonform" = patient_results()$valid_treatment
    )

    # set I and P&I to NA if P doesn't match the patient
    t[!t$P, c("Leitlinienkonform")] <- NA

    return(t)
  })



  observeEvent(rv$patient_id(), {
    print("patient id changed")
  })

  output$guideline_text <- renderUI({
    HTML(guidelines[guidelines$id == input$guideline_id, ]$text)
  })


  observeEvent(input$guideline_id, {
    print("guideline_id changed")

    updateSelectInput(session, "ward", choices = c("Alle", unique(patient_results()$ward)))

    guideline_variables <- load_guideline_variables(input$guideline_id)

    vars_population <- guideline_variables %>%
      filter(type == "population") %>%
      pull(variable_name) %>%
      unique() %>%
      as.list()
    vars_intervention <- guideline_variables %>%
      filter(type == "exposure") %>%
      pull(variable_name) %>%
      unique() %>%
      as.list()

    ##### Create divs######
    output$population_main <- getPlotUIs(vars_population, "population")
    setPlotUIOutputs(output, patientdata, vars_population, "population")
    output$intervention_main <- getPlotUIs(vars_intervention, "intervention")
    setPlotUIOutputs(output, patientdata, vars_intervention, "intervention")
  })
}

shinyApp(ui = ui, server = server)
