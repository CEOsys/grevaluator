library(shiny)

ui <- shinyUI(fluidPage(
  sidebarPanel(
    actionButton("add_btn", "Add Textbox"),
    actionButton("rm_btn", "Remove Textbox"),
    textOutput("counter")
  ),
  mainPanel(
    fluidRow(
      column(6, uiOutput("selectbox_ui"), offset = 0),
      column(6, fluidRow(column(6, uiOutput("textbox_ui1"), uiOutput("textbox_ui2"))),
        fluidRow(column(6, uiOutput("textbox_ui3"), uiOutput("textbox_ui4"), offset = 0)),
        offset = 0
      )
    )
  )
))


server <- shinyServer(function(input, output, session) {
  session$onSessionEnded(stopApp)

  # Track the number of input boxes to render
  counter <- reactiveValues(n = 0)

  observeEvent(input$add_btn, {
    counter$n <- counter$n + 1
  })
  observeEvent(input$rm_btn, {
    if (counter$n > 0) counter$n <- counter$n - 1
  })

  output$counter <- renderPrint(print(counter$n))

  textboxes1 <- reactive({
    n <- counter$n
    if (n > 0) {
      lapply(seq_len(n), function(i) {
        textInput(inputId = paste0("textin1", i), label = paste0("Textbox_A_Topic", i), value = "Hello World!")
      })
    }
  })

  textboxes2 <- reactive({
    n <- counter$n
    if (n > 0) {
      lapply(seq_len(n), function(i) {
        textInput(inputId = paste0("textin2", i), label = paste0("Textbox_B_Topic", i), value = "Hello World!")
      })
    }
  })
  textboxes3 <- reactive({
    n <- counter$n
    if (n > 0) {
      lapply(seq_len(n), function(i) {
        textInput(inputId = paste0("textin3", i), label = paste0("Textbox_C_Topic", i), value = "Hello World!")
      })
    }
  })
  textboxes4 <- reactive({
    n <- counter$n
    if (n > 0) {
      lapply(seq_len(n), function(i) {
        textInput(inputId = paste0("textin4", i), label = paste0("Textbox_D_Topic", i), value = "Hello World!")
      })
    }
  })
  selectboxes <- reactive({
    n <- counter$n
    if (n > 0) {
      lapply(seq_len(n), function(i) {
        selectInput(
          inputId = paste0("selectTopic", i), label = paste0("Topic", i),
          choices = c("one", "two", "three"), selected = "two", multiple = FALSE
        )
      })
    }
  })

  output$textbox_ui1 <- renderUI(textboxes1())
  output$textbox_ui2 <- renderUI({
    textboxes2()
  })
  output$textbox_ui3 <- renderUI({
    textboxes3()
  })
  output$textbox_ui4 <- renderUI({
    textboxes4()
  })
  output$selectbox_ui <- renderUI({
    selectboxes()
  })
})

shinyApp(ui = ui, server = server)
