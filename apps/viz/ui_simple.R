library(shiny)
library(ggplot2)
library(shinythemes)
library(DT)
library(eeptools)
library(tidyverse)
library(dplyr)
library(jsonlite)
library(httr)

source("load_data.R")

load("hosplist_simple.Rdata")

# as.Date(as.POSIXct)


tabldspl <- data.frame(
  "Name" = patient_results$pseudo_fallnr,
  "Alter" = patient_results$age,
  "ITSTag" = patient_results$icu_day,
  "P" = patient_results$valid_population,
  "I" = patient_results$valid_exposure,
  "Leitlinienkonform" = patient_results$valid_treatment
)

ui <- fluidPage(
  themeSelector(),
  theme = shinytheme("united"),

  #*************************************************************************
  # Title Row

  fluidRow(
    column(5, selectInput(
      inputId = "ward", label = "Station",
      choices = c("Alle", unique(patient_results$ward)),
      selected = patient_results$ward[1],
      width = "80%"
    ),
    align = "center"
    ),
    column(1, img(src = "logo_ceosys.jpg", height = 70), align = "left"),
    column(1, img(src = "logo_num.jpg", height = 70), align = "right"),
    column(5, selectInput(
      inputId = "guideline_id", label = "Leitlinie",
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
        DT::dataTableOutput("x11"),
        verbatimTextOutput("y11")
      )
    ),

    # Guideline Column

    column(
      7,

      # Guideline-Text Row

      wellPanel(
        verbatimTextOutput("verb"),
        tags$head(tags$style("#verb{font-size:12px; font-style:italic;overflow-y:scroll; max-height: 20%; background: ghostwhite;}")),
        uiOutput("lllink")
      ),

      # Guideline-Population Row

      wellPanel(
        fluidRow(
          column(2, uiOutput("out_sidepopu1")),
          column(10, uiOutput("out_mainpopu1"))
        ),
        fluidRow(
          column(2, uiOutput("out_sidepopu2")),
          column(10, uiOutput("out_mainpopu2"))
        )
      ),

      # Guideline-Intervention Row

      wellPanel(
        fluidRow(
          column(2, uiOutput("out_sideintv")),
          column(10, uiOutput("out_mainintv"))
        )
      )
    )
  )
)


############# Server ############
server <- function(input, output, session) {

  # Functions for left column
  rward <- reactive({
    input$ward
  })

  # Patient data table
  options(DT.options = list(pageLength = 20))
  observeEvent(rward(), {
    if (input$ward == "Alle") {
      tabldat <- tabldspl
    }
    else {
      tabldat <- tabldspl[patdat$Ward == rward(), ]
    }

    output$x11 <- DT::renderDataTable(
      server = FALSE,
      DT::datatable(tabldat,
        rownames = FALSE,
        selection = "single",
        colnames = c("Name", "Alter", "ITS-Tag ", "P", "I", "P&I erfüllt"),
        options = list(
          columnDefs = list(list(
            render = JS(
              "function(data, type, row, meta) {",
              "if (type === 'display') {",
              "  if (data == true) {",
              "    return '&#10004;'",
              "  } else if (data == false) {",
              "    return '&#x2718;'",
              "  }",
              "}",
              "return data",
              "}"
            ),
            className = "dt-center", targets = 1:5
          ))
        )
      ) %>% formatStyle(c(4:6),
        backgroundColor = styleEqual(
          c(TRUE, FALSE),
          c(
            rgb(200, 230, 200, 255, 255, 255),
            rgb(230, 200, 200, 255, 255, 255)
          )
        )
      )
    )
    output$y11 <- renderPrint(cat(c("Pat. ", tabldat[input$x11_rows_selected, ]$Name, " selected.")))
  })


  ##### Functions for right column #####
  output$verb <- renderText({
    guidelines[guidelines$id == input$guideline_id, ]$text
  })


  observeEvent(input$guideline_id, {
    if (guidelines$id[2] == input$guideline_id) {
      # Diese Informationen werden zukünftig direkt durch LL-Endpoint definiert
      variables <- unique(data$variable_name)
      popu <- c(as.character(variables))[!grepl("drug", variables, fixed = TRUE)]
      intv <- "Dexamethason"
    }
    else {
      popu <- c("Population 1", "Population 2", "Population 3")
      intv <- c("Intervention 1", "Intervention 2")

      popu1 <- c("SpO2", "Oxy Index", "Resp Rate", "Delta-SOFA", "Ventilation Mode")
      popu2 <- c("Adrenaline", "Noradrenaline", "Vasopressine", "Dobutamine", "Dopamine")
    }

    ### This is the function to break the whole data into different blocks for each page
    plotInput <- reactive({
      n_plot <- length(popu)
      total_data <- lapply(1:n_plot, function(i) {
        rnorm(500)
      })
      return(list("n_plot" = n_plot, "total_data" = total_data))
    })

    ##### Create divs######

    output$out_mainpopu1 <- renderUI({
      plot_output_list <- lapply(1, function(i) {
        plotname <- paste("plot", i, sep = "")
        wellPanel(plotOutput(plotname, height = 120, width = 700))
      })
      tagList(plot_output_list)
    })

    output$out_mainpopu2 <- renderUI({
      plot_output_list <- lapply(2, function(i) {
        plotname <- paste("plot", i, sep = "")
        wellPanel(plotOutput(plotname, height = 120, width = 700))
      })
      tagList(plot_output_list)
    })

    output$out_sidepopu1 <- renderUI({
      btn_output_list <- lapply(1, function(i) {
        checkboxGroupInput("checkGroupPop1",
          label = "",
          choices = list(
            "SpO2" = 1,
            "Oxy Index" = 1,
            "Resp Rate" = 1,
            "Delta-SOFA" = 1,
            "Ventilation Mode" = 1
          ),
          selected = 1
        )
      })
      tagList(btn_output_list)
    })

    output$out_sidepopu2 <- renderUI({
      btn_output_list <- lapply(2, function(i) {
        checkboxGroupInput("checkGroupPop2",
          label = "",
          choices = list(
            "Adrenaline" = 1,
            "Noradrenaline" = 1,
            "Vasopressine" = 1,
            "Dobutamine" = 1,
            "Dopamine" = 1
          ),
          selected = 1
        )
      })
      tagList(btn_output_list)
    })

    observe({
      lapply(1:length(popu), function(i) {
        output[[paste("plot", i, sep = "")]] <- renderPlot({
          par(fig = c(0, 1, 0, 1), new = TRUE, mar = c(2, 2, 2, 2))
          hist(plotInput()$total_data[[i]], main = paste(popu[i]))
          par(fig = c(0.9, 1, 0, 1), new = TRUE, mar = c(2, 0, 2, 0))
          boxplot(plotInput()$total_data[[i]], axes = FALSE)
        })
      })
    })

    ## Intervention Row

    output$out_mainintv <- renderUI({
      plot_output_list <- lapply(3, function(i) {
        plotname <- paste("plot", i, sep = "")
        wellPanel(plotOutput(plotname, height = 120, width = 700))
      })
      tagList(plot_output_list)
    })

    output$out_sideintv <- renderUI({
      checkboxGroupInput("chk_sideintv", " ", intv)
    })

    output$out_sideintv <- renderUI({
      btn_output_list <- lapply(3, function(i) {
        checkboxGroupInput("checkGroupInt",
          label = "",
          choices = list("Dexamethason" = 1),
          selected = 1
        )
      })
      tagList(btn_output_list)
    })
  })

  # observeEvent(input$LLsel, {
  #   output$out_plotpopu <- renderPlot({
  #
  #     lbl_top <- "RASS"
  #     x_top <- as.POSIXct(as.character(data[data$variable_name==lbl_top,]$datetime))
  #     y_top <- as.numeric(data[data$variable_name==lbl_top,]$value)
  #
  #     lbl_mid <- "SOFA"
  #     x_mid <- as.POSIXct(as.character(data[data$variable_name==lbl_mid,]$datetime))
  #     y_mid <- as.numeric(data[data$variable_name==lbl_mid,]$value)
  #
  #     if(LL$choices[1]==input$LLsel){
  #       x_btm <- c(1:100)
  #       y_btm <- x_btm*sin(x_btm)
  #       #Bottom
  #       par(fig=c(0, 1, 0, 0.4),new=TRUE, mar = c(2,2,2,2))
  #       plot(x_btm, y_btm, xlab="",ylab="")
  #       abline(v = x_btm[ceiling(length(x_btm)/3)], untf = FALSE)
  #       text(x_btm[ceiling(length(x_btm)/3)],y_btm[ceiling(length(x_btm)/3)]+.1*ceiling(length(x_btm)/3),"   Medi1",adj = c(0,0))
  #     }
  #     if(LL$choices[2]==input$LLsel){
  #       #Bottom
  #       par(fig=c(0, 1, 0, 0.4),new=TRUE, mar = c(2,2,2,2))
  #       plot(x_mid, y_mid, xlab="Time",ylab="")
  #       grid()
  #       #Top
  #       par(fig=c(0, 1, .6, 1),new=TRUE, mar = c(2,2,2,2))
  #       plot(x_top,y_top,ylab=lbl_top,xlab=" ",ylim = c(-5,4))
  #       grid()
  #
  #       par(fig=c(0.9, 1, .6, 1),new=TRUE, mar = c(2,0,2,0))
  #       boxplot(y_top, axes=FALSE)
  #
  #       #Mid
  #       par(fig=c(0 , 1, .3, .7), new=TRUE, mar = c(2,2,2,2))
  #       plot(x_mid, y_mid, ylab=lbl_mid,xlab=" ")
  #       grid()
  #
  #       par(fig=c(0.9, 1, .3, .7),new=TRUE, mar = c(2,0,2,0))
  #       boxplot(y_mid, axes=FALSE)
  #     }
  #
  #   })
  # })
}

shinyApp(ui = ui, server = server)
